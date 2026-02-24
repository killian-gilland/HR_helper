"""
PDF Utils : Lecture Texte Uniquement (Clean Version)
"""
import pypdf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_obj) -> str:
    """Extrait le texte brut du PDF."""
    try:
        reader = pypdf.PdfReader(file_obj)
        text = ""
        for page in reader.pages:
            extract = page.extract_text()
            if extract: text += extract + "\n"
        
        final_text = text.strip()
        
        if len(final_text) < 50:
            return "" 
        return final_text
    except Exception as e:
        logger.error(f"Erreur lecture texte: {e}")
        return ""