import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")

from engine.image_analysis import detect_rooms_from_floorplan_image


def test_detect_rooms_from_synthetic_floorplan():
    img = np.full((500, 700, 3), 255, dtype=np.uint8)

    # Draw two enclosed room-like rectangles.
    cv2.rectangle(img, (60, 80), (300, 360), (0, 0, 0), 5)
    cv2.rectangle(img, (360, 80), (640, 360), (0, 0, 0), 5)
    cv2.line(img, (300, 220), (360, 220), (0, 0, 0), 5)

    ok, buf = cv2.imencode(".png", img)
    assert ok

    result = detect_rooms_from_floorplan_image(buf.tobytes())
    assert result["room_count"] >= 2
    assert result["estimated_sprinklers"] >= 2
    assert result["fallback_used"] is False
