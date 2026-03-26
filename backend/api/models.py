from sqlalchemy import Column, String, Float, Integer, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base
from datetime import datetime

class SensorData(Base):
    __tablename__ = "sensor_data"

    time = Column(TIMESTAMP(timezone=True), primary_key=True)
    station_id = Column(String(50), primary_key=True)
    parameter = Column(String(50), primary_key=True)
    value = Column(Float)
    unit = Column(String(20))
    quality_code = Column(Integer)
    source = Column(String(100))
    meta = Column("metadata", JSONB)

class Prediction(Base):
    __tablename__ = "predictions"

    time = Column(TIMESTAMP(timezone=True), primary_key=True)
    station_id = Column(String(50), primary_key=True)
    model_name = Column(String(100), primary_key=True)
    prediction_type = Column(String(50))
    predicted_value = Column(Float)
    confidence = Column(Float)
    meta = Column("metadata", JSONB)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(TIMESTAMP(timezone=True), nullable=False)
    station_id = Column(String(50), nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(String)
    resolved = Column(Integer, default=0)
    resolved_at = Column(TIMESTAMP(timezone=True))
    meta = Column("metadata", JSONB)
