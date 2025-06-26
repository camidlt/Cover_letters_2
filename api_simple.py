from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import shutil
import os
import json
from datetime import datetime
from pathlib import Path

# Import des modules existants
from parser_cv import extract_cv_content
from generateur_lettre_pdf import generer_lettre
from langdetect import detect

app = FastAPI(title="Générateur de Lettre de Motivation", version="1.0.0")

# Dossier de stockage des CV
CV_STORAGE_DIR = Path("cv_storage")
CV_STORAGE_DIR.mkdir(exist_ok=True)

# Fichier de métadonnées des CV
CV_METADATA_FILE = CV_STORAGE_DIR / "cv_metadata.json"

# Configuration CORS pour permettre les requêtes depuis l'extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API Générateur de Lettre de Motivation"}

@app.post("/generate-letter")
async def generate_letter(
    offre_content: str = Form(...),
    langue: str = Form(...),
    cv_file: UploadFile = File(None),
    cv_id: str = Form(None)
):
    """
    Génère une lettre de motivation à partir d'une offre d'emploi et d'un CV
    Peut utiliser un nouveau CV (cv_file) ou un CV existant (cv_id)
    """
    try:
        cv_content = None
        used_cv_id = None
        
        if cv_id:
            # Utiliser un CV existant
            metadata = load_cv_metadata()
            if cv_id not in metadata:
                raise HTTPException(status_code=404, detail="CV non trouvé")
            
            cv_path = metadata[cv_id]["path"]
            if not os.path.exists(cv_path):
                raise HTTPException(status_code=404, detail="Fichier CV non trouvé")
            
            # Parser le CV existant
            cv_content = extract_cv_content(cv_path)
            used_cv_id = cv_id
            
            # Mettre à jour la date d'utilisation
            metadata[cv_id]["last_used"] = datetime.now().isoformat()
            save_cv_metadata(metadata)
            
        elif cv_file:
            # Utiliser un nouveau CV
            if not cv_file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Le CV doit être un fichier PDF")
            
            # Générer un ID pour le nouveau CV
            used_cv_id = get_or_create_cv_id(cv_file)
            
            # Sauvegarder le nouveau CV
            cv_path = save_cv_file(cv_file, used_cv_id)
            
            # Parser le nouveau CV
            cv_content = extract_cv_content(cv_path)
            
            # Ajouter aux métadonnées
            metadata = load_cv_metadata()
            metadata[used_cv_id] = {
                "id": used_cv_id,
                "original_filename": cv_file.filename,
                "upload_date": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
                "path": cv_path
            }
            save_cv_metadata(metadata)
            
        else:
            raise HTTPException(status_code=400, detail="Aucun CV fourni (cv_file ou cv_id requis)")
        
        # Détecter la langue si pas fournie ou invalide
        if not langue or langue == "auto":
            try:
                langue = detect(offre_content)
            except Exception:
                langue = "en"  # Défaut anglais
        
        # Générer la lettre de motivation (PDF)
        pdf_content = generer_lettre(cv_content, offre_content, langue)
        
        # Retourner le PDF en tant que fichier téléchargeable
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=lettre_motivation.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")

@app.post("/detect-language")
async def detect_language(content: str = Form(...)):
    """
    Détecte la langue d'un texte
    """
    try:
        langue = detect(content)
        return {"langue": langue}
    except Exception as e:
        return {"langue": "en", "error": str(e)}

@app.get("/health")
async def health_check():
    """
    Vérification de l'état de l'API
    """
    return {"status": "healthy", "message": "API fonctionnelle"}

# Fonctions utilitaires pour la gestion des CV
def load_cv_metadata():
    """Charge les métadonnées des CV"""
    if CV_METADATA_FILE.exists():
        with open(CV_METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cv_metadata(metadata):
    """Sauvegarde les métadonnées des CV"""
    with open(CV_METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def save_cv_file(cv_file: UploadFile, cv_id: str):
    """Sauvegarde un fichier CV et retourne le chemin"""
    cv_path = CV_STORAGE_DIR / f"{cv_id}.pdf"
    with open(cv_path, 'wb') as f:
        shutil.copyfileobj(cv_file.file, f)
    return str(cv_path)

def get_or_create_cv_id(cv_file: UploadFile):
    """Génère un ID unique pour le CV ou utilise un existant"""
    # Pour simplifier, on utilise le nom du fichier + timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = cv_file.filename.replace('.pdf', '').replace(' ', '_')
    return f"{filename}_{timestamp}"

@app.get("/cv/list")
async def list_cvs():
    """Liste tous les CV stockés"""
    try:
        metadata = load_cv_metadata()
        # Trier par date d'utilisation (plus récent en premier)
        sorted_cvs = sorted(
            metadata.values(), 
            key=lambda x: x.get('last_used', ''), 
            reverse=True
        )
        return {"cvs": sorted_cvs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des CV: {str(e)}")

@app.post("/cv/upload")
async def upload_cv(cv_file: UploadFile = File(...)):
    """Upload un nouveau CV sans générer de lettre"""
    try:
        # Vérifier que le fichier CV est un PDF
        if not cv_file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Le CV doit être un fichier PDF")
        
        # Générer un ID pour le CV
        cv_id = get_or_create_cv_id(cv_file)
        
        # Sauvegarder le fichier CV
        cv_path = save_cv_file(cv_file, cv_id)
        
        # Mettre à jour les métadonnées
        metadata = load_cv_metadata()
        metadata[cv_id] = {
            "id": cv_id,
            "original_filename": cv_file.filename,
            "upload_date": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "path": cv_path
        }
        save_cv_metadata(metadata)
        
        return {
            "success": True,
            "cv_id": cv_id,
            "message": "CV uploadé avec succès"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
