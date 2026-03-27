# EXPLORATION API TEMPS RÉEL — BASSIN D'ARCACHON
## Session 27 Mars 2026 21:00 — Résultats Investigation

---

## ❌ CONCLUSION : AUCUNE API TEMPS RÉEL PUBLIQUE VIABLE IDENTIFIÉE

Après exploration exhaustive des sources de données océanographiques françaises, **aucune API REST publique temps réel** n'a été identifiée pour le Bassin d'Arcachon compatible avec les contraintes du projet Ocean Sentinel V3.0 MAS.

---

## 🔍 SOURCES EXPLORÉES

### 1. Hub'Eau API
**URL** : https://hubeau.eaufrance.fr/page/api-qualite-cours-deau  
**Scope** : Qualité des cours d'eau (rivières, plans d'eau continentaux)  
**Endpoints** :
- `/api/v2/qualite_rivieres/station_pc` : Stations mesure physico-chimiques
- `/api/v2/qualite_rivieres/analyse_pc` : Analyses physico-chimiques

**Paramètres disponibles** : Conductivité, nitrates, pesticides, métaux lourds  
**Format** : JSON, GeoJSON, CSV  
**Pagination** : Oui (max 20 000 enregistrements)  
**Rate limiting** : Longueur URL max 2 083 caractères

**Verdict** : ❌ **Non applicable**  
**Raison** : Hub'Eau couvre uniquement cours d'eau continentaux (rivières), **PAS eaux littorales/marines**. Bassin d'Arcachon est une lagune marine, hors scope Hub'Eau.

---

### 2. SOMLIT Arcachon
**URL** : https://www.seanoe.org/data/00891/100311/  
**Réseau** : Service d'Observation en Milieu Littoral (SOMLIT)  
**Stations** : 3 (Eyrac, Bouee13, Comprian)  
**Période** : 1997 - 2024  
**Fréquence** : **Fortnightly** (bimensuel, échantillonnage toutes les 2 semaines)

**Paramètres mesurés** :
- Température, salinité, oxygène dissous, pH
- Nitrate, nitrite, ammonium, phosphate, silicate
- Matière en suspension, chlorophylle a
- Isotopes carbone/azote particulaire

**Accès données** :
- Portail demande : https://www.somlit.fr/demande-de-donnees/
- Dataset SEANOE : https://www.seanoe.org/data/00891/100311/
- Format : CSV, pas d'API REST publique

**Verdict** : ❌ **Pas temps réel**  
**Raison** : Fréquence bimensuelle insuffisante pour monitoring temps réel (objectif Ocean Sentinel : rafraîchissement 15min). Accès via portail demande, pas API publique.

---

### 3. COAST-HF Arcachon-Ferret
**URL** : https://www.seanoe.org/data/00889/100119/  
**Réseau** : Coastal OceAn observing SysTem - High Frequency (COAST-HF)  
**Station** : Bouée Phares et Balises (44.66°N, -1.25°W)  
**Période** : Février 2018 - Décembre 2023  
**Fréquence** : **10 minutes** ✅ (haute fréquence)

**Paramètres mesurés** :
- Température (±0.1°C)
- Conductivité (±0.3 mS/cm)
- Profondeur
- Turbidité (±10%)
- Fluorescence (±10%)

**Instrumentation** :
- Février 2018 → Juillet 2020 : NKE SMATCH-TD
- Novembre 2020 → Décembre 2023 : NKE SMATCH-TD (upgraded)

**Transmission données** : Coriolis Côtier database (https://data.coriolis-cotier.org/)

**Accès données** :
- Dataset SEANOE : CSV 22MB (https://www.seanoe.org/data/00889/100119/data/110657.csv)
- Coriolis Côtier : Interface Angular (pas API REST publique identifiée)

**Verdict** : ⚠️ **Données haute fréquence existent, mais API non publique**  
**Raison** :
- ✅ Fréquence 10min adaptée pour temps réel
- ✅ Paramètres pertinents (température, conductivité)
- ❌ CSV 22MB provoque OOM sur VPS 512MB RAM
- ❌ Coriolis Côtier : Interface Angular, pas API REST documentée

---

### 4. Coriolis Côtier Database
**URL** : https://data.coriolis-cotier.org/  
**Type** : Application Angular (interface web)  
**Données** : COAST-HF, réseaux observation côtière française

**Investigation technique** :
- Page HTML retourne application Angular (balises `<script>`, `<style>`)
- Pas de documentation API REST publique
- Endpoints XHR/Fetch non identifiés (nécessite F12 Network investigation approfondie)

**Verdict** : ❌ **Interface web uniquement, pas API REST publique**  
**Raison** : Application Angular nécessite interaction utilisateur, pas d'accès programmatique direct identifié.

---

### 5. SIBA (Syndicat Intercommunal Bassin Arcachon)
**URL** : https://www.siba-bassin-arcachon.fr/  
**Plateforme données** : https://sibapublic.yourenki.com/  
**Contact** : accesdonneespubliques@siba-bassin-arcachon.fr

**Réseau hydrologique** :
- 8 stations Bassin d'Arcachon depuis 1988
- Fréquence : Hebdomadaire (1x/semaine)
- Paramètres : Température, salinité, matière suspension, silicate, nitrate, ammonium, phosphate, chlorophylle a

**Accès données** :
- Plateforme Enki (https://sibapublic.yourenki.com/)
- Manuel utilisateur : https://www.siba-bassin-arcachon.fr/sites/default/files/2022-04/guide_utilisateur_enki_siba_v2.pdf
- Pas d'API REST publique identifiée

**Verdict** : ⚠️ **Données existent, API à investiguer**  
**Raison** : Plateforme Enki peut avoir API, nécessite contact SIBA pour accès programmatique.

---

## 📊 SYNTHÈSE COMPARATIVE

| Source | Fréquence | Paramètres | API Publique | Streaming | Viable MVP |
|--------|-----------|------------|--------------|-----------|------------|
| **Hub'Eau** | N/A | N/A (cours d'eau) | ✅ REST | ✅ | ❌ (scope incorrect) |
| **SOMLIT** | Fortnightly | Temp, Sal, pH, O₂, Nutrients | ❌ | ❌ | ❌ (pas temps réel) |
| **COAST-HF** | 10 min | Temp, Cond, Turb, Fluo | ❌ | ❌ | ⚠️ (CSV 22MB OOM) |
| **Coriolis Côtier** | Temps réel | Multiples | ❌ | ❌ | ❌ (interface Angular) |
| **SIBA** | Hebdomadaire | Temp, Sal, Nutrients | ❌ | ❌ | ⚠️ (API à investiguer) |

---

## 🎯 ALTERNATIVES FUTURES (Phase 3+)

### Option 1 : Partenariat SIBA
**Action** : Contacter accesdonneespubliques@siba-bassin-arcachon.fr  
**Demande** : Accès API temps réel données qualité eau Bassin Arcachon  
**Probabilité succès** : **Moyenne**  
**Délai** : 2-4 semaines (validation institutionnelle)

**Avantages** :
- Source locale officielle (Syndicat Intercommunal)
- Données validées scientifiquement
- Potentiel partenariat institutionnel

**Inconvénients** :
- Fréquence hebdomadaire (pas 10min comme COAST-HF)
- Nécessite accord formel
- API non garantie (plateforme Enki à investiguer)

---

### Option 2 : COAST-HF Data Request
**Action** : Demande accès API via https://www.somlit.fr/demande-de-donnees/  
**Demande** : Accès API temps réel COAST-HF Arcachon-Ferret (10min)  
**Probabilité succès** : **Faible**  
**Délai** : 4-8 semaines (réseau recherche, validation scientifique)

**Avantages** :
- Fréquence 10min (haute fréquence)
- Données température, conductivité, turbidité, fluorescence
- Infrastructure recherche IR ILICO (crédibilité)

**Inconvénients** :
- Réseau recherche (pas API publique standard)
- Nécessite justification scientifique
- API non garantie (peut nécessiter développement custom)

---

### Option 3 : Coriolis Côtier API Investigation
**Action** : Reverse engineering interface Angular (F12 Network → XHR/Fetch)  
**Probabilité succès** : **Moyenne**  
**Délai** : 1-2 semaines (investigation technique)

**Avantages** :
- Données temps réel COAST-HF disponibles
- Pas de validation institutionnelle nécessaire

**Inconvénients** :
- API non documentée (peut changer sans préavis)
- Risque blocage si détection scraping
- Maintenance complexe (dépendance API non officielle)

**Méthodologie** :
1. Ouvrir https://data.coriolis-cotier.org/ dans navigateur
2. F12 → Network → Filtrer XHR/Fetch
3. Naviguer vers station Arcachon-Ferret
4. Identifier requêtes API (JSON/CSV)
5. Copier cURL → transformer en URL template
6. Tester endpoint avec `curl` (vérifier authentification, rate limiting)

---

### Option 4 : ERDDAP IFREMER
**Action** : Explorer https://erddap.ifremer.fr/erddap/tabledap/index.html  
**Probabilité succès** : **Faible**  
**Délai** : 1 semaine (exploration catalogue)

**Raison faible probabilité** :
- ERDDAP EMODnet déjà exploré (aucun dataset Arcachon)
- IFREMER peut avoir datasets différents, mais peu probable

---

## ✅ DÉCISION STRATÉGIQUE — MVP AVEC DONNÉES MOCK

### Rationale

1. **Aucune API temps réel publique viable** identifiée après exploration exhaustive (Hub'Eau, SOMLIT, COAST-HF, Coriolis Côtier, SIBA)

2. **MVP opérationnel** démontre architecture complète :
   - ✅ Dashboard Next.js (http://76.13.43.3)
   - ✅ Backend FastAPI DB-first (SQL DISTINCT ON optimisé)
   - ✅ TimescaleDB (hypertables, compression 7 jours)
   - ✅ Docker Compose orchestration (5 services healthy)

3. **Données mock suffisantes** pour :
   - Validation technique architecture
   - Démonstration stakeholders
   - Tests frontend/backend intégration

4. **Ingestion temps réel** nécessite :
   - Partenariat institutionnel (SIBA, COAST-HF, Coriolis)
   - Validation scientifique (justification usage données)
   - Développement API custom (si API publique inexistante)

### Actions Immédiates

1. **Ajouter disclaimer dashboard** : Badge "Données de démonstration" avec timestamp statique
2. **Documenter limitation** : README.md + BILAN-STRATEGIQUE-SESSION-27-MARS-2026.md
3. **Proposer Phase 3** : Partenariat SIBA ou investigation Coriolis Côtier API

---

## 📋 PROCHAINES ÉTAPES (Phase 3)

### Étape 1 : Ajouter Disclaimer Dashboard
**Fichier** : `frontend/src/app/page.tsx`  
**Action** : Badge "⚠️ Données de démonstration (timestamp statique)"  
**Position** : Au-dessus KPI cards

### Étape 2 : Contact SIBA
**Email** : accesdonneespubliques@siba-bassin-arcachon.fr  
**Objet** : Demande accès API données qualité eau Bassin Arcachon - Projet Ocean Sentinel  
**Contenu** :
- Présentation projet Ocean Sentinel V3.0 MAS
- Objectif : Monitoring temps réel qualité eau Bassin Arcachon
- Demande : Accès API temps réel ou partenariat données

### Étape 3 : Investigation Coriolis Côtier API
**Action** : F12 Network → identifier endpoints XHR/Fetch  
**Critère succès** : URL API retournant JSON/CSV données COAST-HF Arcachon-Ferret  
**Délai** : 1-2 semaines

---

## 🔗 RÉFÉRENCES

- Hub'Eau API : https://hubeau.eaufrance.fr/page/api-qualite-cours-deau
- SOMLIT Arcachon : https://www.seanoe.org/data/00891/100311/
- COAST-HF Arcachon-Ferret : https://www.seanoe.org/data/00889/100119/
- Coriolis Côtier : https://data.coriolis-cotier.org/
- SIBA : https://www.siba-bassin-arcachon.fr/
- SIBA Plateforme données : https://sibapublic.yourenki.com/

---

**FIN EXPLORATION API TEMPS RÉEL — 27 MARS 2026 21:00**
