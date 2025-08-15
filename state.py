from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class CarState:
    position_m: float = 0.0
    speed_mps: float = 0.0
    gear: int = 1
    rpm: float = 1000.0
    throttle: float = 0.0
    brake: float = 0.0
    steering_deg: float = 0.0
    fuel_l: float = 0.0
    tyre_wear: float = 0.0
    lap: int = 1
    time_s: float = 0.0


@dataclass
class TelemetryEvent:
    timestamp_iso: str
    carId: str
    driver: str
    team: str
    lap: int
    gate: Optional[int]
    split_time: Optional[float]
    speed_kmh: float
    rpm: int
    gear: int
    throttle: float
    brake: float
    steering_deg: float
    fuel_l: float
    tyre_wear: float
    lap_time: Optional[float]
    stint_time: float
    extra: Dict = field(default_factory=dict)
