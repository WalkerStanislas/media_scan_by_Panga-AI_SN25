@echo off
REM Script de démarrage rapide du Dashboard MÉDIA-SCAN pour Windows
REM Usage: start_dashboard.bat

echo ==========================================
echo   MÉDIA-SCAN Dashboard - Démarrage
echo ==========================================
echo.

REM Vérifier que nous sommes dans le bon répertoire
if not exist "dashboard\app.py" (
    echo ❌ Erreur: Ce script doit être exécuté depuis la racine du projet
    echo    Veuillez vous placer dans le répertoire du projet et réessayer
    pause
    exit /b 1
)

REM Vérifier l'environnement virtuel
if not exist "venv" (
    echo ⚠️  Environnement virtuel non trouvé
    echo    Création de l'environnement virtuel...
    python -m venv venv
)

REM Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Vérifier que streamlit est installé
where streamlit >nul 2>nul
if %errorlevel% neq 0 (
    echo 📦 Installation des dépendances...
    pip install -r requirements.txt
)

REM Vérifier la présence des données
if not exist "data\processed\sample_data.json" (
    echo ⚠️  Fichier de données exemple non trouvé
    echo    Assurez-vous d'avoir des données dans data\processed\
)

echo.
echo ✅ Tout est prêt!
echo.
echo 🚀 Lancement du dashboard...
echo    Le dashboard va s'ouvrir dans votre navigateur
echo    URL: http://localhost:8501
echo.
echo 💡 Pour arrêter: Appuyez sur Ctrl+C
echo.
echo ==========================================
echo.

REM Lancer le dashboard
streamlit run dashboard\app.py