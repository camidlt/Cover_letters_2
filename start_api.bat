@echo off
echo 🚀 Démarrage du serveur API pour le générateur de lettre de motivation
echo =====================================================================

echo Installation des dépendances...
pip install fastapi uvicorn python-multipart

echo.
echo Démarrage du serveur sur http://localhost:8000
echo Pour arrêter le serveur, appuyez sur Ctrl+C
echo.

cd backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
