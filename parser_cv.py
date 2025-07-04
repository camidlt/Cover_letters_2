import fitz  # PyMuPDF

def extract_cv_content(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    return text.strip()