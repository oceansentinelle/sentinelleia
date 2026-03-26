from __future__ import annotations
import csv
import os
from datetime import datetime, timezone
from io import StringIO
import requests

from .base import SensorRecord, Connector

def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

class ERDDAPConnector(Connector):
    """
    ERDDAP via URL template. Expected to return CSV with a 'time' column + one column per variable.
    Example columns: time,TEMP,PSAL,PH,DOX2
    """
    def __init__(self) -> None:
        self.url_template = os.getenv("ERDDAP_URL_TEMPLATE", "").strip()
        self.source_name = os.getenv("ERDDAP_SOURCE_NAME", "ERDDAP")
        self.timeout = int(os.getenv("HTTP_TIMEOUT_SECONDS", "20"))

        # mapping variable->(parameter, unit)
        self.var_map = {
            "TEMP": ("temperature", "°C"),
            "PSAL": ("salinity", "PSU"),
            "PH":   ("ph", "pH"),
            "DOX2": ("dissolved_oxygen", "mg/L"),
        }

    def fetch(self, station_id: str, start: datetime, end: datetime):
        if not self.url_template or "{start_iso}" not in self.url_template or "{end_iso}" not in self.url_template:
            raise RuntimeError("ERDDAP_URL_TEMPLATE missing or must include {start_iso} and {end_iso}")

        url = self.url_template.format(start_iso=_iso(start), end_iso=_iso(end))
        headers = {"User-Agent": "OceanSentinel/3.0 (ERDDAP ingestor)"}

        r = requests.get(url, headers=headers, timeout=self.timeout)
        r.raise_for_status()

        text = r.text
        buf = StringIO(text)
        reader = csv.DictReader(buf)

        out = []
        for row in reader:
            if "time" not in row or not row["time"]:
                continue
            t = datetime.fromisoformat(row["time"].replace("Z", "+00:00"))

            for var, (param, unit) in self.var_map.items():
                v = row.get(var)
                if v is None or v == "" or v.lower() == "nan":
                    continue
                try:
                    fv = float(v)
                except ValueError:
                    continue

                out.append(SensorRecord(
                    time=t,
                    station_id=station_id,
                    parameter=param,
                    value=fv,
                    unit=unit,
                    quality_code=1,
                    source=self.source_name,
                    meta={"raw_var": var},
                ))
        return out
