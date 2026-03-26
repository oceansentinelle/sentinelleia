from __future__ import annotations
import os
import json
import csv
from io import StringIO
from datetime import datetime, timezone
import requests

from .base import SensorRecord, Connector

def _ms(dt: datetime) -> int:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.astimezone(timezone.utc).timestamp() * 1000)

def _parse_time(x) -> datetime | None:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return datetime.fromtimestamp(float(x)/1000.0, tz=timezone.utc)
    s = str(x)
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

class CoriolisPlatformConnector(Connector):
    """
    Very tolerant parser: accepts JSON dict/list or CSV with time column.
    """
    def __init__(self) -> None:
        self.url_template = os.getenv("CORIOLIS_URL_TEMPLATE", "").strip()
        self.source_name = os.getenv("CORIOLIS_SOURCE_NAME", "Coriolis/Platform")
        self.timeout = int(os.getenv("HTTP_TIMEOUT_SECONDS", "20"))
        self.headers = {"User-Agent": "OceanSentinel/3.0 (Coriolis ingestor)"}

        self.map = {
            "TEMP": ("temperature", "°C"),
            "temperature": ("temperature", "°C"),
            "PSAL": ("salinity", "PSU"),
            "salinity": ("salinity", "PSU"),
            "PH": ("ph", "pH"),
            "ph": ("ph", "pH"),
            "DOX2": ("dissolved_oxygen", "mg/L"),
            "dissolved_oxygen": ("dissolved_oxygen", "mg/L"),
            "TURB": ("turbidity", "NTU"),
            "turbidity": ("turbidity", "NTU"),
            "FLU2": ("fluorescence", "RFU"),
            "fluorescence": ("fluorescence", "RFU"),
        }

    def fetch(self, station_id: str, start: datetime, end: datetime):
        if not self.url_template or "{start_ms}" not in self.url_template or "{end_ms}" not in self.url_template:
            raise RuntimeError("CORIOLIS_URL_TEMPLATE missing or must include {start_ms} and {end_ms}")

        url = self.url_template.format(start_ms=_ms(start), end_ms=_ms(end))
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        r.raise_for_status()

        ctype = (r.headers.get("content-type") or "").lower()
        text = r.text

        if "text/csv" in ctype or text.lstrip().startswith("time,") or text.lstrip().startswith("timestamp,"):
            reader = csv.DictReader(StringIO(text))
            return self._from_rows(station_id, reader)

        try:
            obj = r.json()
        except Exception:
            raise RuntimeError(f"Unexpected response (not JSON/CSV). content-type={ctype}")

        rows = None
        if isinstance(obj, dict):
            for k in ("data", "rows", "result", "values"):
                if k in obj and isinstance(obj[k], list):
                    rows = obj[k]
                    break
        elif isinstance(obj, list):
            rows = obj

        if rows and all(isinstance(x, dict) for x in rows):
            return self._from_rows(station_id, rows)

        if isinstance(obj, dict) and any(isinstance(v, list) for v in obj.values()):
            return self._from_columnar(station_id, obj)

        raise RuntimeError("Unrecognized Coriolis payload structure (need mapping).")

    def _from_rows(self, station_id: str, rows):
        out = []
        for row in rows:
            t = _parse_time(row.get("time") or row.get("timestamp") or row.get("date"))
            if not t:
                continue
            for key, val in row.items():
                if key in ("time", "timestamp", "date"):
                    continue
                if val in (None, "", "NaN", "nan"):
                    continue
                try:
                    fv = float(val)
                except Exception:
                    continue
                if key in self.map:
                    param, unit = self.map[key]
                    out.append(SensorRecord(t, station_id, param, fv, unit=unit, quality_code=1, source=self.source_name, meta={"raw_var": key}))
        return out

    def _from_columnar(self, station_id: str, obj: dict):
        time_key = "time" if "time" in obj else ("timestamp" if "timestamp" in obj else None)
        if not time_key:
            raise RuntimeError("Columnar payload missing time/timestamp key")
        times = obj[time_key]
        out = []
        for raw_var, series in obj.items():
            if raw_var == time_key or raw_var not in self.map or not isinstance(series, list):
                continue
            param, unit = self.map[raw_var]
            for i, v in enumerate(series):
                t = _parse_time(times[i]) if i < len(times) else None
                if not t or v in (None, "", "NaN", "nan"):
                    continue
                try:
                    fv = float(v)
                except Exception:
                    continue
                out.append(SensorRecord(t, station_id, param, fv, unit=unit, quality_code=1, source=self.source_name, meta={"raw_var": raw_var}))
        return out
