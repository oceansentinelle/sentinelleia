# Infrastructure Ocean Sentinel V3.0 MAS

**Date** : 26 mars 2026  
**Agent** : DevOps

---

## Architecture Docker Compose

### Services Déployés

#### TimescaleDB (PostgreSQL 14)
- **Image** : `timescale/timescaledb:latest-pg14`
- **Port** : 5432
- **Mémoire** : 2GB (limite)
- **Volumes** : 
  - `timescaledb_data` : Données persistantes
  - `init.sql` : Initialisation base de données
- **Features** :
  - Hypertables (chunks 1 jour)
  - Compression automatique (7 jours)
  - Agrégats continus (statistiques horaires)
  - Rétention 1 an

#### Nginx (Alpine)
- **Image** : `nginx:alpine`
- **Ports** : 80 (HTTP), 443 (HTTPS)
- **Mémoire** : 128MB (limite)
- **Features** :
  - Reverse proxy (API + Frontend)
  - Rate limiting (10 req/s)
  - Gzip compression
  - Health check endpoint

---

## Déploiement

### Prérequis
- Docker 29.3.1+
- Docker Compose v5.1.1+
- Fichier `.env.production` configuré

### Commandes

**Démarrer infrastructure** :
```bash
cd ~/apps/ocean-sentinel-main/infra
docker compose --env-file ../.env.production up -d
```

**Vérifier statut** :
```bash
docker compose ps
docker compose logs -f
```

**Arrêter infrastructure** :
```bash
docker compose down
```

**Arrêter + supprimer volumes** :
```bash
docker compose down -v
```

---

## Configuration

### Variables d'environnement (.env.production)

```env
# PostgreSQL/TimescaleDB
POSTGRES_USER=oceansentinel
POSTGRES_PASSWORD=<généré aléatoirement>
POSTGRES_DB=ocean_sentinel_prod
POSTGRES_HOST=timescaledb
POSTGRES_PORT=5432

# Docker Resources
DB_MEMORY_LIMIT=2g
NGINX_MEMORY_LIMIT=128m
```

---

## Base de Données

### Tables Créées

**sensor_data** (hypertable)
- Données capteurs temps réel
- Compression après 7 jours
- Rétention 1 an
- Index : station_id, parameter, time

**sensor_data_hourly** (continuous aggregate)
- Statistiques horaires (avg, min, max, stddev)
- Rafraîchissement automatique toutes les heures

**predictions** (hypertable)
- Prédictions modèles ML
- Chunks 1 jour

**alerts** (table standard)
- Alertes écologiques
- Index : time, station_id, resolved

### Connexion Base de Données

```bash
docker exec -it ocean-timescaledb psql -U oceansentinel -d ocean_sentinel_prod
```

**Requêtes utiles** :
```sql
-- Voir données récentes
SELECT * FROM sensor_data ORDER BY time DESC LIMIT 10;

-- Statistiques horaires
SELECT * FROM sensor_data_hourly ORDER BY bucket DESC LIMIT 10;

-- Vérifier compression
SELECT * FROM timescaledb_information.chunks WHERE is_compressed = true;
```

---

## Monitoring

### Health Checks

**Nginx** :
```bash
curl http://localhost/health
# Réponse attendue: "healthy"
```

**TimescaleDB** :
```bash
docker exec ocean-timescaledb pg_isready -U oceansentinel
# Réponse attendue: "accepting connections"
```

### Logs

**Tous les services** :
```bash
docker compose logs -f
```

**Service spécifique** :
```bash
docker compose logs -f timescaledb
docker compose logs -f nginx
```

---

## Maintenance

### Backup Base de Données

```bash
docker exec ocean-timescaledb pg_dump -U oceansentinel ocean_sentinel_prod > backup_$(date +%Y%m%d).sql
```

### Restore Base de Données

```bash
cat backup_20260326.sql | docker exec -i ocean-timescaledb psql -U oceansentinel ocean_sentinel_prod
```

### Nettoyage Docker

```bash
# Supprimer images inutilisées
docker image prune -a

# Supprimer volumes orphelins
docker volume prune
```

---

## Troubleshooting

### TimescaleDB ne démarre pas

**Vérifier logs** :
```bash
docker compose logs timescaledb
```

**Vérifier permissions** :
```bash
ls -la timescaledb/init.sql
```

### Nginx erreur 502 Bad Gateway

**Vérifier backend disponible** :
```bash
docker compose ps
```

**Vérifier configuration** :
```bash
docker exec ocean-nginx nginx -t
```

### Mémoire insuffisante

**Vérifier utilisation** :
```bash
docker stats
free -h
```

**Ajuster limites dans `.env.production`** :
```env
DB_MEMORY_LIMIT=1g
NGINX_MEMORY_LIMIT=64m
```

---

## Prochaines Étapes

1. Ajouter service `backend` (FastAPI)
2. Ajouter service `frontend` (Next.js)
3. Configurer SSL/TLS (Certbot)
4. Activer reverse proxy Nginx (décommenter config)
5. Monitoring Prometheus + Grafana

---

**Documentation complète** : `INFRASTRUCTURE_AUDIT.md`
