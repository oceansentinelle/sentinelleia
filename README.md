# Ocean Sentinel V3.0 — Multi-Agent System (MAS)

**Plateforme d'Intelligence Artificielle Prédictive pour la Surveillance Océanique**

## 🌊 Vision

Ocean Sentinel V3.0 est un système multi-agents (MAS) conçu pour analyser en temps réel la qualité de l'eau du Bassin d'Arcachon via des données océanographiques (Hub'Eau, bouées CAPENA). Le système transforme les relevés de capteurs en intelligence écologique exploitable pour protéger l'ostréiculture et les écosystèmes marins.

## 🏗️ Architecture Multi-Agent System (MAS)

Le projet est structuré autour de **6 agents spécialisés** :

### 1. Agent Architecte
- Design système et architecture globale
- Définition des interfaces inter-agents
- Gouvernance technique

### 2. Agent Data Engineer
- Pipelines ETL (Extract, Transform, Load)
- Connecteurs API Hub'Eau / CAPENA
- Gestion TimescaleDB (séries temporelles)

### 3. Agent Scientifique
- Calculs océanographiques UNESCO (PSS-78, Nernst, Garcia & Gordon)
- Validation scientifique des données
- Métriques environnementales

### 4. Agent IA
- Entraînement modèles ML (LSTM, Random Forest)
- Inférence prédictive (pH, O₂, salinité)
- Détection d'anomalies (Isolation Forest)

### 5. Agent Frontend
- Interface utilisateur React/Vite
- Dashboard temps réel
- Visualisations interactives

### 6. Agent DevOps
- Infrastructure Docker/Docker Compose
- CI/CD GitHub Actions
- Monitoring Prometheus/Grafana

## 🚀 Stack Technique

- **Backend** : FastAPI (Python 3.11)
- **Frontend** : React + Vite + TailwindCSS
- **Database** : TimescaleDB (PostgreSQL 14)
- **ML** : ONNX Runtime (LSTM, Random Forest)
- **Infra** : Docker Compose, Nginx, Certbot
- **Monitoring** : Prometheus, Grafana Cloud

## 📁 Structure Projet

```
sentinelleia/
├── agents/              # 6 agents MAS
│   ├── architecte/
│   ├── data_engineer/
│   ├── scientifique/
│   ├── ia/
│   ├── frontend/
│   └── devops/
├── backend/             # API FastAPI
├── frontend/            # React/Vite
├── infra/               # Docker, Nginx, TimescaleDB
├── scripts/             # Automation, backup
└── docs/                # Documentation
```

## 🎯 Stratégie Dual-Domain

- **oceansentinelle.fr** : Plateforme SaaS IA (produit monétisable)
- **oceansentinelle.org** : Plateforme éducative (SEO, crédibilité)

## 📊 Modèle Économique

- **Freemium** : Dashboard public, données 7 jours
- **Premium** (9.99€/mois) : Historique complet, API, alertes
- **B2B** (sur devis) : API entreprise, support dédié

## 🔒 Sécurité

- SSH port personnalisé (61189)
- Authentification par clé SSH uniquement
- Firewall UFW strict (ports 22, 80, 443)
- Secrets gérés via `.env.production`

## 🎯 État MVP Actuel

**Plateforme opérationnelle** : http://76.13.43.3

**Stack déployée** :
- ✅ Dashboard Next.js 16 (interface temps réel)
- ✅ Backend FastAPI (API DB-first, SQL optimisé)
- ✅ TimescaleDB (hypertables, compression 7 jours)
- ✅ Nginx reverse proxy
- ✅ Docker Compose orchestration (5 services)

**Données affichées** :
- Station BARAG - Bassin d'Arcachon
- Paramètres : Température, Salinité, pH, O₂ dissous
- Source : Données de démonstration (timestamp statique)

**⚠️ Limitation Ingestion Temps Réel** :

Après exploration exhaustive des sources de données océanographiques françaises (Hub'Eau, SOMLIT, COAST-HF, Coriolis Côtier, SIBA), **aucune API REST publique temps réel** n'a été identifiée pour le Bassin d'Arcachon compatible avec les contraintes du projet.

**Alternatives Phase 3** :
- Partenariat SIBA (accesdonneespubliques@siba-bassin-arcachon.fr)
- Investigation Coriolis Côtier API (reverse engineering)
- COAST-HF data request (https://www.somlit.fr/demande-de-donnees/)

Voir [EXPLORATION-API-TEMPS-REEL-ARCACHON.md](EXPLORATION-API-TEMPS-REEL-ARCACHON.md) pour détails complets.

## 📝 Documentation

- [Architecture MAS](docs/architecture-mas.md)
- [Déploiement](docs/deployment.md)
- [Infrastructure Audit](INFRASTRUCTURE_AUDIT.md)
- [Exploration API Temps Réel](EXPLORATION-API-TEMPS-REEL-ARCACHON.md)
- [Bilan Stratégique Session 27 Mars](BILAN-STRATEGIQUE-SESSION-27-MARS-2026.md)

## 👥 Équipe

- **SACS** : Superviseur Multi-Agent System
- **Cascade AI** : Agent DevOps intégré Windsurf IDE

## � Remerciements

**« Ce travail a bénéficié du soutien de l'Infrastructure de Recherche Littorale et Côtière : IR ILICO ».**

## �📜 Licence

MIT License — Ocean Sentinel V3.0 (2026)
