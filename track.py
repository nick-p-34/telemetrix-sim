from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Segment:
    name: str
    typ: str
    length: float
    radius: Optional[float] = None
    direction: Optional[str] = None
    cumulative_start: float = 0.0
    cumulative_end: float = 0.0


SEGMENTS: List[Segment] = []

_cum = 0.0


def add_segment(name, typ, length, radius=None, direction=None):
    global _cum
    seg = Segment(name=name, typ=typ, length=length, radius=radius, direction=direction,
                  cumulative_start=_cum, cumulative_end=_cum + length)
    SEGMENTS.append(seg)
    _cum += length


add_segment("Start/Finish Straight", "straight", 700.000)
add_segment("T1 Right Hairpin", "arc", 94.248, radius=45.0, direction='R')
add_segment("Short Straight A", "straight", 90.000)
add_segment("T2 Right Tight", "arc", 85.018, radius=65.0, direction='R')
add_segment("T3 Left Kink", "arc", 27.925, radius=40.0, direction='L')
add_segment("Medium Straight", "straight", 250.0)
add_segment("T4 S-entry R", "arc", 79.419, radius=70.0, direction='R')
add_segment("T5 Esses L", "arc", 62.832, radius=60.0, direction='L')
add_segment("T6 Right Sweep", "arc", 235.619, radius=150.0, direction='R')
add_segment("Back Straight", "straight", 900.0)
add_segment("Chicane", "arc", 35.391, radius=30.0, direction='L')
add_segment("T7 Left Medium", "arc", 76.771, radius=80.0, direction='L')
add_segment("Short Straight B", "straight", 120.0)
add_segment("T8 Right Hairpin", "arc", 99.492, radius=38.0, direction='R')
add_segment("T9 Left Sweep", "arc", 146.607, radius=120.0, direction='L')
add_segment("Long Right HighSpeed", "arc", 365.184, radius=220.0, direction='R')
add_segment("Infield Straight", "straight", 400.0)
add_segment("T10 Left Tight", "arc", 69.813, radius=50.0, direction='L')
add_segment("T11 Right Kink", "arc", 18.330, radius=35.0, direction='R')
add_segment("Complex Esses", "arc", 116.938, radius=50.0, direction='L')
add_segment("Pre-Finish Straight", "straight", 500.0)
add_segment("Final Curve Left", "arc", 139.626, radius=160.0, direction='L')
add_segment("T12 Right Mega-Sweep", "arc", 628.319, radius=300.0, direction='R')
add_segment("Straight C", "straight", 360.0)
add_segment("Final Connector", "straight", 350.000)

LAP_LENGTH = SEGMENTS[-1].cumulative_end

GATE_DISTANCES = [
    198.374, 396.749, 595.123, 793.497, 991.872, 1190.246, 1388.620, 1586.995, 1785.369, 1983.743,
    2182.118, 2380.492, 2578.866, 2777.240, 2975.615, 3173.989, 3372.363, 3570.738, 3769.112, 3967.486,
    4165.861, 4364.235, 4562.609, 4760.984, 4959.358, 5157.732, 5356.107, 5554.481, 5752.856, 0.0
]
GATES = {i + 1: GATE_DISTANCES[i] for i in range(30)}
