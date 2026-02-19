"""
LLM Analysis Module - SMART LOCAL (Llama3 + LLaVA)
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
        # On définit deux modèles selon le besoin
        self.vision_model = "llava"   # Pour les images
        self.text_model = "llama3"    # Pour le texte (Beaucoup plus intelligent)

    def generate_content(self, inputs):
        """Aiguillage intelligent : Texte -> Llama3, Image -> LLaVA"""
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
        # Si on a une image, on est obligé d'utiliser LLaVA
        # Si c'est juste du texte (PDF), on utilise Llama3 (Bien meilleur)
        selected_model = self.vision_model if has_image else self.text_model

        # 3. Configuration de la requête
        payload = {
            "model": selected_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "images": images,
            "options": {
                "temperature": 0.0, # Zéro créativité
                "num_ctx": 4096
            }
        }

        try:
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
            # On augmente la qualité pour aider LLaVA à lire
            image.save(buf, format="PNG") 
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        except:
            return None

    @property
    def client(self): return self

def create_analyzer():
    return LLMAnalyzer()