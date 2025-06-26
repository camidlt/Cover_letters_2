# 📝 Générateur de Lettre de Motivation - Extension Chrome

## 🚀 Installation et utilisation

### 1. Installation des dépendances Python

```bash
pip install -r requirements.txt
```

### 2. Démarrage de l'API

**Option A : Script automatique (Windows)**
```bash
./start_api.bat
```

**Option B : Manuel**
```bash
cd backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

L'API sera disponible sur : http://localhost:8000

### 3. Installation de l'extension Chrome

1. Ouvrez Chrome et allez dans : `chrome://extensions/`
2. Activez le "Mode développeur" (en haut à droite)
3. Cliquez sur "Charger l'extension non empaquetée"
4. Sélectionnez le dossier `extension/`
5. L'extension apparaît dans la barre d'outils Chrome

### 4. Utilisation

1. **Démarrez l'API** avec `start_api.bat`
2. **Naviguez** vers une offre d'emploi (JobTeaser, LinkedIn, Indeed, etc.)
3. **Cliquez** sur l'icône de l'extension dans Chrome
4. **Uploadez** votre CV (PDF)
5. **Cliquez** sur "Générer la lettre de motivation"
6. **Téléchargez** automatiquement la lettre générée

## 🎯 Fonctionnalités

✅ **Extraction automatique** du contenu des offres d'emploi  
✅ **Détection automatique** de la langue  
✅ **Interface intuitive** dans Chrome  
✅ **Téléchargement automatique** de la lettre  
✅ **Support multi-sites** (JobTeaser, LinkedIn, Indeed, etc.)  
✅ **Aucun problème de captcha** ou JavaScript  

## 🔧 Dépannage

### L'extension ne détecte pas l'offre
- Vérifiez que vous êtes sur une page d'offre d'emploi
- Rechargez la page et réessayez
- L'indicateur vert "Extension active" doit apparaître

### L'API ne répond pas
- Vérifiez que le serveur est démarré (`start_api.bat`)
- Vérifiez l'adresse : http://localhost:8000/health
- Redémarrez le serveur si nécessaire

### Problème d'upload de CV
- Vérifiez que le fichier est bien un PDF
- Taille maximale : 10MB

## 📁 Structure du projet

```
Cover_letters_2/
├── backend/
│   └── api.py              # API FastAPI
├── extension/
│   ├── manifest.json       # Configuration extension
│   ├── popup.html          # Interface utilisateur
│   ├── popup.js           # Logique interface
│   └── content.js         # Extraction contenu
├── parser_cv.py           # Parser CV (existant)
├── generateur_lettre.py   # Générateur (existant)
├── requirements.txt       # Dépendances
└── start_api.bat         # Script de démarrage
```

## 🎉 Avantages de cette approche

- **Plus de problème de parsing** (extraction directe depuis la page)
- **Plus rapide** (pas de Selenium)
- **Interface moderne** et intuitive
- **Compatible tous navigateurs**
- **Facile à distribuer**
