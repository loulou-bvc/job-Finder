#!/bin/bash

# Script de lancement pour macOS
echo "🚀 Lancement de l'application de gestion d'offres de stage"
echo "=================================================="

# Vérifier Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trouvé. Veuillez installer Python 3.7+"
    exit 1
fi

# Aller dans le répertoire du script
cd "$(dirname "$0")"

# Lancer l'application
echo "🎯 Lancement de l'application..."
python3 start_app.py

echo "👋 Application fermée"
