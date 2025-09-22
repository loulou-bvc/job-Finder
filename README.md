# 🚀 Gestionnaire d'Offres de Stage V2

Application complète pour la recherche et gestion d'offres de stage avec interface graphique moderne.

## ✨ Fonctionnalités

- **Interface graphique moderne** avec Tkinter
- **Scraping automatique** HelloWork et Indeed
- **Filtrage avancé** avec recherche en temps réel
- **Statistiques détaillées** avec graphiques
- **Export des données** en CSV
- **Configuration centralisée** en JSON
- **Base de données SQLite** intégrée

## 🚀 Lancement Rapide

### Option 1 : Script automatique (macOS)
```bash
./start.sh
```

### Option 2 : Python direct
```bash
python3 start_app.py
```

### Option 3 : Installation des dépendances
```bash
pip install -r requirements.txt
python3 main_app_v2.py
```

## 📊 Fonctionnalités Principales

### 🕷️ Scraping
- **HelloWork** : Scraping automatique des offres
- **Indeed** : Intégration avec Indeed
- **Configuration** : Délais, pages max, mots-clés
- **Logs en temps réel** : Suivi du processus

### 📋 Gestion des Offres
- **Affichage tabulaire** : Vue claire des offres
- **Filtrage avancé** : Par domaine, ville, mots-clés
- **Détails complets** : Double-clic pour voir les détails
- **Ouverture URL** : Accès direct aux offres

### 📊 Statistiques
- **Vue d'ensemble** : Total, domaines, villes
- **Graphiques** : Visualisation avec matplotlib
- **Export** : Données en CSV avec timestamp

### ⚙️ Configuration
- **Paramètres scraping** : Délais, pages
- **Interface** : Thème, taille fenêtre
- **Sauvegarde** : Configuration persistante

## 📁 Structure du Projet

```
job-Finder/
├── main_app_v2.py          # Application principale
├── start_app.py            # Script de lancement
├── start.sh               # Script bash (macOS)
├── requirements.txt       # Dépendances Python
├── config_default.json    # Configuration par défaut
├── database.py            # Gestion base de données
├── scraper_offres.py      # Scraper HelloWork
├── scrapper_indeed.py     # Scraper Indeed
├── visu.py               # Interface de visualisation
└── data/                 # Bases de données SQLite
    └── offres.db
```

## 🛠️ Dépendances

- **Python 3.7+** requis
- **Tkinter** : Interface graphique (inclus avec Python)
- **SQLite3** : Base de données (inclus avec Python)
- **requests** : Requêtes HTTP
- **beautifulsoup4** : Parsing HTML
- **selenium** : Scraping avancé
- **matplotlib** : Graphiques
- **pandas** : Manipulation données

## 🎯 État du Projet

✅ **Application fonctionnelle** et prête à l'utilisation !
✅ **Interface moderne** avec tous les outils nécessaires
✅ **Base de données** intégrée et fonctionnelle
✅ **Scraping** configuré pour HelloWork et Indeed
✅ **Export/Import** des données
✅ **Configuration** flexible et persistante

## 🚀 Prochaines Améliorations

- [ ] Intégration complète des scrapers
- [ ] Système de candidatures
- [ ] Notifications automatiques
- [ ] API REST
- [ ] Interface web
