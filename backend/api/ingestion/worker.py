from __future__ import annotations
import os
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from api.database import SessionLocal
from api.models import SensorData
from .erddap import ERDDAPConnector

GET_STATE = text("""
SELECT last_time FROM ingestion_state
WHERE source=:source AND station_id=:station_id
""")

UPSERT_STATE = text("""
INSERT INTO ingestion_state(source, station_id, last_time)
VALUES(:source, :station_id, :last_time)
ON CONFLICT (source, station_id) DO UPDATE
SET last_time = EXCLUDED.last_time, updated_at = NOW()
""")

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def get_connector():
    src = os.getenv("DATA_SOURCE", "erddap").lower()
    if src == "erddap":
        return ERDDAPConnector()
    if src == "coriolis_platform":
        from .coriolis_platform import CoriolisPlatformConnector
        return CoriolisPlatformConnector()
    if src == "seanoe":
        from .seanoe import SEANOEConnector
        return SEANOEConnector()
    raise RuntimeError(f"Unsupported DATA_SOURCE={src}")

def read_last_time(db: Session, source: str, station_id: str):
    row = db.execute(GET_STATE, {"source": source, "station_id": station_id}).scalar_one_or_none()
    return row

def save_last_time(db: Session, source: str, station_id: str, last_time: datetime):
    db.execute(UPSERT_STATE, {"source": source, "station_id": station_id, "last_time": last_time})
    db.commit()

def insert_records(db: Session, records):
    if not records:
        return 0

    rows = [{
        "time": r.time,
        "station_id": r.station_id,
        "parameter": r.parameter,
        "value": r.value,
        "unit": r.unit,
        "quality_code": r.quality_code,
        "source": r.source,
        "metadata": r.meta,
    } for r in records]

    stmt = pg_insert(SensorData.__table__).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=["time", "station_id", "parameter"])
    res = db.execute(stmt)
    db.commit()
    return res.rowcount or 0

def main():
    station_id = os.getenv("STATION_ID", "BARAG")
    interval = int(os.getenv("INGEST_INTERVAL_SECONDS", "900"))
    lookback_min = int(os.getenv("INGEST_LOOKBACK_MINUTES", "60"))

    connector = get_connector()
    source_name = os.getenv("ERDDAP_SOURCE_NAME", "ERDDAP")

    print(f"[ingestor] start station={station_id} interval={interval}s source={source_name}", flush=True)

    while True:
        t0 = utcnow()
        try:
            with SessionLocal() as db:
                last = read_last_time(db, source_name, station_id)
                start = last or (t0 - timedelta(minutes=lookback_min))
                end = t0

                records = list(connector.fetch(station_id=station_id, start=start, end=end))
                n = insert_records(db, records)

                if records:
                    max_time = max(r.time for r in records)
                    save_last_time(db, source_name, station_id, max_time)

                print(f"[ingestor] fetched={len(records)} inserted={n} window={start.isoformat()}..{end.isoformat()}", flush=True)

        except Exception as e:
            print(f"[ingestor][error] {e}", flush=True)

        dt = (utcnow() - t0).total_seconds()
        sleep_s = max(5, interval - int(dt))
        time.sleep(sleep_s)

if __name__ == "__main__":
    main()
