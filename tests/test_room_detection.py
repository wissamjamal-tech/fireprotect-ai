from engine.room_detector import detect_rooms_from_polylines


def test_nested_room_detection_ignores_outer_envelope():
    outer = [(0, 0), (12, 0), (12, 10), (0, 10), (0, 0)]
    r1 = [(1, 1), (5, 1), (5, 4), (1, 4), (1, 1)]
    r2 = [(6, 1), (11, 1), (11, 4), (6, 4), (6, 1)]

    rooms = detect_rooms_from_polylines([outer, r1, r2])
    # outer envelope should be filtered as false-positive container
    assert len(rooms) == 2
