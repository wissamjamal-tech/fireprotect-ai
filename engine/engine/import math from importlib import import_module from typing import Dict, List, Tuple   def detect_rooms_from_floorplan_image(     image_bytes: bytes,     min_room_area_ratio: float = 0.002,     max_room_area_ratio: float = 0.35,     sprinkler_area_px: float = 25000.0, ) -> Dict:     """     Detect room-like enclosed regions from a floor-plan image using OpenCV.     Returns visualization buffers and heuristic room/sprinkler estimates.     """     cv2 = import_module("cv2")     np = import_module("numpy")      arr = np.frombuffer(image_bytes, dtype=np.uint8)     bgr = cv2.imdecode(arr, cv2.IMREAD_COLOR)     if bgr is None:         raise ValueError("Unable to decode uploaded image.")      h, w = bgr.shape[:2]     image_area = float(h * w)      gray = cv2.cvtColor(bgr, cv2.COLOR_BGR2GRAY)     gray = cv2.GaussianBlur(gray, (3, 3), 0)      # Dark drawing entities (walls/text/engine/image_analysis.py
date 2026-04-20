import math
from importlib import import_module
from typing import Dict, List, Tuple


def detect_rooms_from_floorplan_image(
    image_bytes: bytes,
    min_room_area_ratio: float = 0.002,
    max_room_area_ratio: float = 0.35,
    sprinkler_area_px: float = 25000.0,
) -> Dict:
    """
    Detect room-like enclosed regions from a floor-plan image using OpenCV.
    Returns visualization buffers and heuristic room/sprinkler estimates.
    """
    cv2 = import_module("cv2")
    np = import_module("numpy")

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError("Unable to decode uploaded image.")

    h, w = bgr.shape[:2]
    image_area = float(h * w)

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Dark drawing entities (walls/text/furniture) become white in line mask.
    line_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]
    line_mask = cv2.morphologyEx(line_mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))
    line_mask = cv2.dilate(line_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)

    # Candidate open spaces are everything except linework.
    free_space = cv2.bitwise_not(line_mask)
    flood = free_space.copy()
    ff_mask = np.zeros((h + 2, w + 2), np.uint8)
    # Remove outside/open background by flood-filling from border.
    cv2.floodFill(flood, ff_mask, (0, 0), 0)
    enclosed = flood

    contours, _ = cv2.findContours(enclosed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    room_contours: List = []
    room_areas_px: List[float] = []

    min_area = image_area * min_room_area_ratio
    max_area = image_area * max_room_area_ratio

    for cnt in contours:
        area = float(cv2.contourArea(cnt))
        if area < min_area or area > max_area:
            continue

        x, y, bw, bh = cv2.boundingRect(cnt)
        if bw < 30 or bh < 30:
            continue

        # Ignore long narrow regions and common tiny symbols.
        aspect = max(bw / max(bh, 1), bh / max(bw, 1))
        if aspect > 8.0:
            continue

        perimeter = cv2.arcLength(cnt, True)
        if perimeter <= 0:
            continue

        compactness = 4.0 * math.pi * area / (perimeter * perimeter)
        if compactness < 0.06:
            continue

        room_contours.append(cnt)
        room_areas_px.append(area)

    edges = cv2.Canny(gray, 60, 160)
    edge_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    room_overlay = bgr.copy()
    if room_contours:
        cv2.drawContours(room_overlay, room_contours, -1, (0, 165, 255), 2)

    # Room-based heuristic estimate (preliminary, not engineering-grade).
    sprinklers_per_room = [max(1, int(math.ceil(a / sprinkler_area_px))) for a in room_areas_px]
    estimated_sprinklers = int(sum(sprinklers_per_room))

    # Fallback when room detection is weak or fails.
    fallback_used = False
    if not room_contours:
        fallback_used = True
        estimated_sprinklers = max(1, int(math.ceil(image_area / 180000.0)))

    ok1, edge_png = cv2.imencode(".png", edge_bgr)
    ok2, room_png = cv2.imencode(".png", room_overlay)
    if not ok1 or not ok2:
        raise RuntimeError("Failed to encode preview images.")

    return {
        "room_count": len(room_contours),
        "estimated_sprinklers": estimated_sprinklers,
        "fallback_used": fallback_used,
        "edge_preview_png": edge_png.tobytes(),
        "rooms_preview_png": room_png.tobytes(),
    }
