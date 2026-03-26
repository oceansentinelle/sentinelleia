from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta
import os

from .database import get_db, engine
from .models import Base, SensorData, Alert

app = FastAPI(
    title="Ocean Sentinel API",
    description="API temps réel pour données océanographiques - Bouée BARAG Arcachon",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    pass

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ocean-sentinel-api",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/v1/iob/card")
async def get_iob_card(db: Session = Depends(get_db)):
    try:
        latest_data = db.query(SensorData).filter(
            SensorData.station_id == "BARAG"
        ).order_by(desc(SensorData.time)).limit(20).all()
        
        if not latest_data:
            return {
                "station_id": "BARAG",
                "station_name": "Bouée BARAG - Bassin d'Arcachon",
                "last_update": None,
                "parameters": {},
                "predictions": {
                    "temperature": {"value": None, "trend": "stable", "confidence": 0},
                    "salinity": {"value": None, "trend": "stable", "confidence": 0},
                    "ph": {"value": None, "trend": "stable", "confidence": 0},
                    "dissolved_oxygen": {"value": None, "trend": "stable", "confidence": 0}
                },
                "alerts": []
            }
        
        parameters = {}
        latest_time = None
        
        for record in latest_data:
            if latest_time is None or record.time > latest_time:
                latest_time = record.time
            
            param_key = record.parameter
            if param_key not in parameters:
                parameters[param_key] = {
                    "value": record.value,
                    "unit": record.unit,
                    "quality_code": record.quality_code,
                    "timestamp": record.time.isoformat()
                }
        
        active_alerts = db.query(Alert).filter(
            Alert.station_id == "BARAG",
            Alert.resolved == 0
        ).order_by(desc(Alert.time)).limit(5).all()
        
        alerts_list = [
            {
                "id": alert.id,
                "type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.time.isoformat()
            }
            for alert in active_alerts
        ]
        
        predictions = {
            "temperature": {
                "value": parameters.get("temperature", {}).get("value"),
                "trend": "stable",
                "confidence": 0.85
            },
            "salinity": {
                "value": parameters.get("salinity", {}).get("value"),
                "trend": "stable",
                "confidence": 0.82
            },
            "ph": {
                "value": parameters.get("ph", {}).get("value"),
                "trend": "stable",
                "confidence": 0.88
            },
            "dissolved_oxygen": {
                "value": parameters.get("dissolved_oxygen", {}).get("value"),
                "trend": "stable",
                "confidence": 0.80
            }
        }
        
        return {
            "station_id": "BARAG",
            "station_name": "Bouée BARAG - Bassin d'Arcachon",
            "last_update": latest_time.isoformat() if latest_time else None,
            "parameters": parameters,
            "predictions": predictions,
            "alerts": alerts_list,
            "metadata": {
                "source": "Hub'Eau Quadrige",
                "location": "Bassin d'Arcachon",
                "coordinates": {"lat": 44.6667, "lon": -1.1667}
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/v1/stations")
async def get_stations(db: Session = Depends(get_db)):
    try:
        stations = db.query(SensorData.station_id).distinct().all()
        return {
            "stations": [{"id": s[0], "name": f"Station {s[0]}"} for s in stations]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/v1/sensor-data/{station_id}")
async def get_sensor_data(
    station_id: str,
    parameter: str = None,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(SensorData).filter(
            SensorData.station_id == station_id,
            SensorData.time >= time_threshold
        )
        
        if parameter:
            query = query.filter(SensorData.parameter == parameter)
        
        data = query.order_by(desc(SensorData.time)).all()
        
        return {
            "station_id": station_id,
            "parameter": parameter,
            "period_hours": hours,
            "count": len(data),
            "data": [
                {
                    "time": record.time.isoformat(),
                    "parameter": record.parameter,
                    "value": record.value,
                    "unit": record.unit,
                    "quality_code": record.quality_code
                }
                for record in data
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
