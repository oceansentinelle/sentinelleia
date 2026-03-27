from __future__ import annotations
import os
import csv
from datetime import datetime, timezone
from io import StringIO
import requests

from .base import SensorRecord, Connector

def _parse_time(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return None

def _parse_qc(qc_str: str) -> int:
    if not qc_str or len(qc_str) < 1:
        return 0
    try:
        return int(qc_str[0])
    except Exception:
        return 0

class SEANOEConnector(Connector):
    """
    SEANOE COAST-HF/Arcachon-Ferret CSV connector.
    Downloads complete CSV file and filters by last_time for incremental ingestion.
    """
    def __init__(self) -> None:
        self.url = os.getenv("SEANOE_URL", "").strip()
        self.source_name = os.getenv("SEANOE_SOURCE_NAME", "COAST-HF/Arcachon-Ferret")
        self.timeout = int(os.getenv("HTTP_TIMEOUT_SECONDS", "60"))
        self.headers = {"User-Agent": "OceanSentinel/3.0 (SEANOE ingestor)"}

        self.column_map = {
            "TEMP LEVEL1": ("temperature", "°C"),
            "PSAL LEVEL1": ("salinity", "PSU"),
            "FLU2 LEVEL1": ("fluorescence", "mg/m³"),
            "TUR4 LEVEL1": ("turbidity", "NTU"),
        }

    def fetch(self, station_id: str, start: datetime, end: datetime):
        if not self.url:
            raise RuntimeError("SEANOE_URL missing in environment")

        r = requests.get(self.url, headers=self.headers, timeout=self.timeout, stream=True)
        r.raise_for_status()

        text = r.text
        reader = csv.DictReader(StringIO(text))

        out = []
        for row in reader:
            date_str = row.get("DATE (yyyy-mm-ddThh:mi:ssZ)")
            if not date_str:
                continue

            t = _parse_time(date_str)
            if not t:
                continue

            if t < start:
                continue

            qc_str = row.get("QC", "")
            qc = _parse_qc(qc_str)

            for col_name, (param, unit) in self.column_map.items():
                val_str = row.get(col_name)
                if not val_str:
                    continue

                try:
                    fv = float(val_str)
                except ValueError:
                    continue

                if fv < -9000:
                    continue

                out.append(SensorRecord(
                    time=t,
                    station_id=station_id,
                    parameter=param,
                    value=fv,
                    unit=unit,
                    quality_code=qc,
                    source=self.source_name,
                    meta={"platform": row.get("PLATFORM"), "raw_col": col_name},
                ))

        return out
