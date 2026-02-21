"""
LLM Analysis Module - SMART LOCAL (Llama3.2 + LLaVA)
Version Optimisée pour la vitesse (CPU-friendly)
"""

import json
import logging
import requests
import base64
from io import BytesIO
import streamlit as st

logger = logging.getLogger(__name__)

class ResponseWrapper:
    def __init__(self, text):
        self.text = text

class LLMAnalyzer:
    def __init__(self):
        self.api_url = "http://localhost:11434/api/generate"
        self.vision_model = "llava"   # Pour les images
        # ⚡ CHANGEMENT MAJEUR : llama3.2 (3B) est 3x plus rapide que llama3 (8B)
        self.text_model = "llama3.2"  

    def generate_content(self, inputs):
        """Aiguillage intelligent : Texte -> Llama3.2, Image -> LLaVA"""
        prompt = ""
        images = []
        has_image = False

        # 1. Analyse de l'entrée pour choisir le cerveau
        if isinstance(inputs, list):
            for item in inputs:
                if isinstance(item, str):
                    prompt += item + "\n"
                elif hasattr(item, 'save'): # C'est une image
                    img_b64 = self._image_to_base64(item)
                    if img_b64: 
                        images.append(img_b64)
                        has_image = True
        elif isinstance(inputs, str):
            prompt = inputs

        # 2. Choix du modèle
        selected_model = self.vision_model if has_image else self.text_model

        # 3. Configuration de la requête (Optimisée pour la vitesse)
        payload = {
            "model": selected_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "keep_alive": "1h", # ⚡ Garde le modèle en mémoire (évite le rechargement lent)
            "images": images,
            "options": {
                "temperature": 0.0,
                "num_ctx": 4096,
                "num_predict": 1000 # ⚡ Coupe l'IA si elle parle trop (gain de temps)
            }
        }

        try:
            # On laisse un timeout large au cas où le premier chargement soit long
            response = requests.post(self.api_url, json=payload, timeout=300) 
            
            if response.status_code == 200:
                json_resp = response.json()
                return ResponseWrapper(json_resp.get("response", ""))
            else:
                return ResponseWrapper(f'{{"error": "Erreur Ollama {response.status_code}"}}')

        except Exception as e:
            st.toast(f"🚨 Vérifiez que 'ollama run {selected_model}' a été fait !", icon="🛑")
            return ResponseWrapper('{"nom": "Erreur Connexion", "reasoning": "Modèle introuvable ?", "score": 0}')

    def _image_to_base64(self, image):
        try:
            buf = BytesIO()
            if image.mode in ("RGBA", "P"): image = image.convert("RGB")
            # Qualité réduite légèrement pour accélérer le traitement visuel
            image.save(buf, format="JPEG", quality=85) 
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        except:
            return None

    @property
    def client(self): return self

def create_analyzer():
    return LLMAnalyzer()