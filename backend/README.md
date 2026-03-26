# Backend FastAPI - Ocean Sentinel V3.0 MAS

**Date** : 26 mars 2026  
**Agent** : Backend API

---

## Architecture

### Stack Technique
- **Framework** : FastAPI 0.109.0
- **ORM** : SQLAlchemy 2.0.25
- **Database Driver** : psycopg2-binary 2.9.9
- **Server** : Uvicorn 0.27.0
- **Python** : 3.11-slim

### Endpoints API

#### Health Check
```
GET /health
```
**Réponse** :
```json
{
  "status": "healthy",
  "service": "ocean-sentinel-api",
  "version": "3.0.0",
  "timestamp": "2026-03-26T19:00:00.000000"
}
```

#### IOB Card (Indicateurs Océanographiques Bouée)
```
GET /v1/iob/card
```
**Réponse** :
```json
{
  "station_id": "BARAG",
  "station_name": "Bouée BARAG - Bassin d'Arcachon",
  "last_update": "2026-03-26T18:05:32.385161+00:00",
  "parameters": {
    "temperature": {
      "value": 15.2,
      "unit": "°C",
      "quality_code": 1,
      "timestamp": "2026-03-26T18:05:32.385161+00:00"
    },
    "salinity": {
      "value": 35.1,
      "unit": "PSU",
      "quality_code": 1,
      "timestamp": "2026-03-26T18:05:32.385161+00:00"
    },
    "ph": {
      "value": 8.1,
      "unit": "pH",
      "quality_code": 1,
      "timestamp": "2026-03-26T18:05:32.385161+00:00"
    },
    "dissolved_oxygen": {
      "value": 7.8,
      "unit": "mg/L",
      "quality_code": 1,
      "timestamp": "2026-03-26T18:05:32.385161+00:00"
    }
  },
  "predictions": {
    "temperature": {"value": 15.2, "trend": "stable", "confidence": 0.85},
    "salinity": {"value": 35.1, "trend": "stable", "confidence": 0.82},
    "ph": {"value": 8.1, "trend": "stable", "confidence": 0.88},
    "dissolved_oxygen": {"value": 7.8, "trend": "stable", "confidence": 0.80}
  },
  "alerts": [],
  "metadata": {
    "source": "Hub'Eau Quadrige",
    "location": "Bassin d'Arcachon",
    "coordinates": {"lat": 44.6667, "lon": -1.1667}
  }
}
```

#### Liste Stations
```
GET /v1/stations
```

#### Données Capteurs
```
GET /v1/sensor-data/{station_id}?parameter=temperature&hours=24
```

---

## Modèles SQLAlchemy

### SensorData (Hypertable)
- `time` : TIMESTAMP (primary key)
- `station_id` : VARCHAR(50) (primary key)
- `parameter` : VARCHAR(50) (primary key)
- `value` : FLOAT
- `unit` : VARCHAR(20)
- `quality_code` : INTEGER
- `source` : VARCHAR(100)
- `metadata` : JSONB

### Prediction (Hypertable)
- `time` : TIMESTAMP (primary key)
- `station_id` : VARCHAR(50) (primary key)
- `model_name` : VARCHAR(100) (primary key)
- `prediction_type` : VARCHAR(50)
- `predicted_value` : FLOAT
- `confidence` : FLOAT
- `metadata` : JSONB

### Alert
- `id` : SERIAL (primary key)
- `time` : TIMESTAMP
- `station_id` : VARCHAR(50)
- `alert_type` : VARCHAR(50)
- `severity` : VARCHAR(20)
- `message` : TEXT
- `resolved` : BOOLEAN
- `resolved_at` : TIMESTAMP
- `metadata` : JSONB

---

## Développement Local

### Installation
```bash
cd backend
pip install -r requirements.txt
```

### Variables Environnement
```env
POSTGRES_USER=oceansentinel
POSTGRES_PASSWORD=<password>
POSTGRES_DB=ocean_sentinel_prod
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Lancer Serveur
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Documentation interactive** : http://localhost:8000/docs

---

## Déploiement Docker

### Build Image
```bash
docker build -t ocean-backend:latest .
```

### Run Container
```bash
docker run -d \
  --name ocean-backend \
  -p 8000:8000 \
  -e POSTGRES_USER=oceansentinel \
  -e POSTGRES_PASSWORD=<password> \
  -e POSTGRES_DB=ocean_sentinel_prod \
  -e POSTGRES_HOST=timescaledb \
  -e POSTGRES_PORT=5432 \
  ocean-backend:latest
```

### Docker Compose
```bash
cd ../infra
docker compose up -d backend
```

---

## Tests API

### Health Check
```bash
curl http://localhost:8000/health
```

### IOB Card
```bash
curl http://localhost:8000/v1/iob/card | jq
```

### Stations
```bash
curl http://localhost:8000/v1/stations | jq
```

### Sensor Data
```bash
curl "http://localhost:8000/v1/sensor-data/BARAG?parameter=temperature&hours=24" | jq
```

---

## Connexion Database

### Configuration
- **Pool size** : 10 connexions
- **Max overflow** : 20 connexions
- **Pool pre-ping** : Activé (vérification connexion avant utilisation)

### Session Management
```python
from api.database import get_db

def my_endpoint(db: Session = Depends(get_db)):
    # db session auto-managed (commit/rollback/close)
    pass
```

---

## CORS

**Configuration** : Allow all origins (à restreindre en production)

```python
allow_origins=["*"]  # TODO: Restreindre aux domaines .fr et .org
```

---

## Prochaines Étapes

1. Ajouter authentification JWT
2. Implémenter rate limiting (Redis)
3. Ajouter endpoints ML predictions
4. Intégrer MLflow model serving
5. Monitoring Prometheus metrics
6. Tests unitaires (pytest)

---

**Documentation complète** : http://localhost:8000/docs (Swagger UI)
