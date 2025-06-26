import subprocess
from fpdf import FPDF

def generer_lettre(cv, offre, langue):
    # Mapper les codes de langue vers des noms complets
    langue_mapping = {
        'en': 'anglais',
        'fr': 'français',
        'es': 'espagnol',
        'de': 'allemand',
        'it': 'italien'
    }
    
    langue_complete = langue_mapping.get(langue, langue)
    
    # Exemples de début de lettre pour guider le modèle
    exemples_debut = {
        'en': "Dear Hiring Manager,\n\nI am writing to express my interest...",
        'fr': "Madame, Monsieur,\n\nJe me permets de vous adresser...",
        'es': "Estimado/a responsable de contratación,\n\nMe dirijo a ustedes para expresar...",
        'de': "Sehr geehrte Damen und Herren,\n\nHiermit bewerbe ich mich...",
        'it': "Egregio responsabile delle assunzioni,\n\nMi rivolgo a voi per esprimere..."
    }
    
    exemple = exemples_debut.get(langue, exemples_debut['en'])
    
    prompt = f"""You are an HR assistant. You MUST write a cover letter in {langue_complete}.
CRITICAL: The entire letter MUST be written in {langue_complete}.

Job offer (detected language: {langue}):
{offre}

CV:
{cv}

Example of how to start in {langue_complete}:
{exemple}

Instructions:
- Write the letter ONLY in {langue_complete}
- Objectif : Around 1000 characters
- Structure: Motivated introduction, profile/position match, conclusion with professional closing
- Use a professional tone adapted to the country's culture
- Ensure every single sentence is in {langue_complete}
- Start directly with the letter content, no explanations
- Write ONLY the letter content, no LaTeX formatting

IMPORTANT: If the job offer is in English, write in English. If in French, write in French.
RESPOND ONLY IN {langue_complete.upper()}!"""

    result = subprocess.run(
        ["ollama", "run", "mistral"],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE
    )
    lettre_content = result.stdout.decode("utf-8").strip()
    
    # Générer le PDF
    return generer_pdf_lettre(lettre_content, langue)

def generer_pdf_lettre(contenu_lettre, langue):
    """
    Génère un PDF professionnel de la lettre de motivation
    """
    
    # Nettoyer le contenu
    contenu_lettre = contenu_lettre.strip()
    
    # Extraire les parties de la lettre
    paragraphes = [p.strip() for p in contenu_lettre.split('\n\n') if p.strip()]
    
    # Formules de politesse par langue
    formules_ouverture = {
        'en': 'Dear Hiring Manager,',
        'fr': 'Madame, Monsieur,',
        'es': 'Estimado/a responsable de contratación,',
        'de': 'Sehr geehrte Damen und Herren,',
        'it': 'Egregio responsabile delle assunzioni,'
    }
    
    formules_fermeture = {
        'en': 'Yours sincerely,',
        'fr': 'Cordialement,',
        'es': 'Atentamente,',
        'de': 'Mit freundlichen Grüßen,',
        'it': 'Cordiali saluti,'
    }
    
    ouverture = formules_ouverture.get(langue, formules_ouverture['en'])
    fermeture = formules_fermeture.get(langue, formules_fermeture['en'])
    
    # Créer le PDF avec FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    
    # En-tête avec informations personnelles
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Camille Dupré La Tour', ln=True, align='R')
    pdf.set_font('Arial', size=10)
    pdf.cell(0, 5, '+33 7 68 05 88 22', ln=True, align='R')
    pdf.cell(0, 5, 'camille.duprelatour@email.com', ln=True, align='R')
    pdf.ln(10)
    
    # Date
    from datetime import datetime
    date_str = datetime.now().strftime('%B %d, %Y')
    if langue == 'fr':
        months_fr = {
            'January': 'janvier', 'February': 'février', 'March': 'mars',
            'April': 'avril', 'May': 'mai', 'June': 'juin',
            'July': 'juillet', 'August': 'août', 'September': 'septembre',
            'October': 'octobre', 'November': 'novembre', 'December': 'décembre'
        }
        for en, fr in months_fr.items():
            date_str = date_str.replace(en, fr)
        date_str = datetime.now().strftime(f'%d {months_fr[datetime.now().strftime("%B")]} %Y')
    
    pdf.set_font('Arial', size=10)
    pdf.cell(0, 5, date_str, ln=True, align='L')
    pdf.ln(10)
    
    
    # Formule d'ouverture
    pdf.set_font('Arial', size=12)
    pdf.cell(0, 8, ouverture, ln=True)
    pdf.ln(5)
    
    # Corps de la lettre
    pdf.set_font('Arial', size=11)
    
    # Traiter chaque paragraphe
    for paragraphe in paragraphes:
        # Supprimer les formules d'ouverture/fermeture si déjà présentes
        if any(formule in paragraphe for formule in formules_ouverture.values()):
            continue
        if any(formule in paragraphe for formule in formules_fermeture.values()):
            continue
        if 'sincerely' in paragraphe.lower() or 'cordialement' in paragraphe.lower():
            continue
            
        # Ajouter le paragraphe avec gestion des sauts de ligne
        lines = paragraphe.split('\n')
        for line in lines:
            if line.strip():
                # Gérer les lignes trop longues
                words = line.strip().split(' ')
                current_line = ''
                for word in words:
                    if pdf.get_string_width(current_line + ' ' + word) < 180:
                        current_line += (' ' + word if current_line else word)
                    else:
                        if current_line:
                            pdf.cell(0, 6, current_line, ln=True)
                        current_line = word
                
                if current_line:
                    pdf.cell(0, 6, current_line, ln=True)
        
        pdf.ln(3)  # Espacement entre paragraphes
    
    # Formule de fermeture
    pdf.ln(5)
    pdf.cell(0, 8, fermeture, ln=True)
    pdf.ln(15)
    
    # Signature
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Camille Dupré La Tour', ln=True)
    
    # Générer le PDF et le retourner comme bytes
    return bytes(pdf.output())
