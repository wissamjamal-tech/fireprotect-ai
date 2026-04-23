from dataclasses import dataclass, field
from typing import List, Optional, Tuple

Point = Tuple[float, float]


@dataclass
class Room:
    id: str
    polygon: List[Point]
    area: float
    centroid: Point
    label: Optional[str] = None
    room_type: str = "unknown"


@dataclass
class Stair:
    id: str
    location: Point
    source_room_id: Optional[str] = None


@dataclass
class Placement:
    kind: str
    location: Point
    room_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)
