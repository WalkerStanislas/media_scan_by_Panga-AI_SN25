#!/bin/bash

# Script de démarrage rapide du Dashboard MÉDIA-SCAN
# Usage: ./start_dashboard.sh

echo "=========================================="
echo "  MÉDIA-SCAN Dashboard - Démarrage"
echo "=========================================="
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "dashboard/app.py" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis la racine du projet"
    echo "   Veuillez vous placer dans le répertoire du projet et réessayer"
    exit 1
fi

# Vérifier l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé"
    echo "   Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier que streamlit est installé
if ! command -v streamlit &> /dev/null; then
    echo "📦 Installation des dépendances..."
    pip install -r requirements.txt
fi

# Vérifier la présence des données
if [ ! -f "data/processed/sample_data.json" ]; then
    echo "⚠️  Fichier de données exemple non trouvé"
    echo "   Assurez-vous d'avoir des données dans data/processed/"
fi

echo ""
echo "✅ Tout est prêt!"
echo ""
echo "🚀 Lancement du dashboard..."
echo "   Le dashboard va s'ouvrir dans votre navigateur"
echo "   URL: http://localhost:8501"
echo ""
echo "💡 Pour arrêter: Appuyez sur Ctrl+C"
echo ""
echo "=========================================="
echo ""

# Lancer le dashboard
streamlit run dashboard/app.py