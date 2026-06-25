from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Ward:
    code: str
    name: str


@dataclass(frozen=True)
class Observation:
    ward: str
    observed_at: str
    ward_name: str
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None
    precipitation: Optional[float] = None
