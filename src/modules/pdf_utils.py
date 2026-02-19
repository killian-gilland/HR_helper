"""
PDF Utils : Lecture Texte + Conversion Image (Fallback)
"""
import pypdf
import logging
import fitz  # C'est PyMuPDF
from PIL import Image
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_obj) -> str:
    """Tente de lire le texte. Renvoie vide si c'est un scan."""
    try:
        reader = pypdf.PdfReader(file_obj)
        text = ""
        for page in reader.pages:
            extract = page.extract_text()
            if extract: text += extract + "\n"
        
        final_text = text.strip()
        
        # Si moins de 50 caractères, on considère que c'est une IMAGE déguisée
        if len(final_text) < 50:
            return "" 
        return final_text
    except Exception as e:
        logger.error(f"Erreur lecture texte: {e}")
        return ""

def convert_pdf_to_images(file_obj):
    """Transforme les pages du PDF en images pour LLaVA."""
    images = []
    try:
        # On rembobine le fichier pour le lire depuis le début
        file_obj.seek(0)
        # On ouvre avec PyMuPDF
        doc = fitz.open(stream=file_obj.read(), filetype="pdf")
        
        for page in doc:
            pix = page.get_pixmap(dpi=150) # 150 DPI suffit pour lire
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            images.append(image)
            
        print(f"📸 Conversion PDF -> {len(images)} Images effectuée.")
        return images
    except Exception as e:
        logger.error(f"Erreur conversion image: {e}")
        return []