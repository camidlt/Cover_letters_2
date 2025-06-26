from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules existants
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser_cv import extract_cv_content
from generateur_lettre_pdf import generer_lettre
from langdetect import detect
import tempfile
import shutil

app = FastAPI(title="Générateur de Lettre de Motivation", version="1.0.0")

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
    cv_file: UploadFile = File(...)
):
    """
    Génère une lettre de motivation à partir d'une offre d'emploi et d'un CV
    """
    try:
        # Vérifier que le fichier CV est un PDF
        if not cv_file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Le CV doit être un fichier PDF")
        
        # Sauvegarder temporairement le fichier CV
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            shutil.copyfileobj(cv_file.file, temp_file)
            temp_cv_path = temp_file.name
        
        try:
            # Parser le CV
            cv_content = extract_cv_content(temp_cv_path)
            
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
            
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_cv_path):
                os.unlink(temp_cv_path)
                
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
