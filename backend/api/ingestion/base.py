from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Protocol, Optional, Dict, Any

@dataclass(frozen=True)
class SensorRecord:
    time: datetime
    station_id: str
    parameter: str
    value: float
    unit: str | None = None
    quality_code: int | None = None
    source: str | None = None
    meta: Dict[str, Any] | None = None

class Connector(Protocol):
    def fetch(self, station_id: str, start: datetime, end: datetime) -> Iterable[SensorRecord]:
        ...
