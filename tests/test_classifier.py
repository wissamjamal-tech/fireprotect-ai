from engine.classifier import classify_rooms
from engine.models import Room


def test_classify_by_text_keyword():
    room = Room(id="R1", polygon=[(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)], area=16, centroid=(2, 2))
    texts = [{"text": "Kitchen", "location": (2, 2)}]
    keywords = {"kitchen": ["kitchen"]}
    out = classify_rooms([room], texts, keywords)
    assert out[0].room_type == "kitchen"
