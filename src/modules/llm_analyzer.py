"""
LLM Analysis Module - HYBRIDE (Groq Cloud + Ollama Local)
Aiguillage : Texte -> Groq (Vitesse extrême) | Image -> LLaVA Local
"""

import json
import logging
import requests
import base64
import os # NOUVEAU
from io import BytesIO
import streamlit as st
from groq import Groq
from dotenv import load_dotenv # NOUVEAU

logger = logging.getLogger(__name__)

# Charge les variables cachées du fichier .env
load_dotenv() 

class ResponseWrapper:
    def __init__(self, text):
        self.text = text

class LLMAnalyzer:
    def __init__(self):
        # --- CONFIGURATION OLLAMA (LOCAL POUR LES IMAGES) ---
        self.api_url = "http://localhost:11434/api/generate"
        self.vision_model = "llava"
        
        # --- CONFIGURATION GROQ (CLOUD POUR LE TEXTE) ---
        # ⚡️ La clé est maintenant chargée de façon sécurisée depuis le système ⚡️
        self.groq_api_key = os.getenv("GROQ_API_KEY") 
        self.groq_text_model = "llama-3.3-70b-versatile"
        
        if not self.groq_api_key:
            logger.error("🚨 Clé GROQ_API_KEY introuvable dans l'environnement !")
            
        try:
            self.groq_client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None
        except Exception as e:
            self.groq_client = None
            logger.error(f"Erreur initialisation Groq : {e}")


    def generate_content(self, inputs):
        """Aiguillage intelligent : Texte -> Groq Cloud, Image -> LLaVA Local"""
        prompt = ""
        images = []
        has_image = False

        # 1. Analyse de l'entrée
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

        # 2. AIGUILLAGE DU TRAITEMENT
        if has_image:
            return self._process_local_vision(prompt, images)
        else:
            return self._process_cloud_text(prompt)

    def _process_cloud_text(self, prompt):
        """Traitement ultra-rapide du texte via Groq API"""
        if not self.groq_client or "METS_TA_VRAIE_CLE_ICI" in self.groq_api_key:
            st.toast("🚨 Clé Groq non configurée ! Remplacement temporaire par une erreur.", icon="🛑")
            return ResponseWrapper('{"nom": "Erreur", "reasoning": "Clé API Groq manquante."}')
            
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Tu dois répondre UNIQUEMENT avec un objet JSON valide. Ne rajoute aucun texte avant ou après."},
                    {"role": "user", "content": prompt}
                ],
                model=self.groq_text_model,
                temperature=0.1,
                # Groq possède un mode JSON natif ultra robuste pour garantir le format !
                response_format={"type": "json_object"} 
            )
            return ResponseWrapper(chat_completion.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Erreur Groq: {str(e)}")
            return ResponseWrapper(f'{{"nom": "Erreur API Groq", "reasoning": "{str(e)}"}}')

    def _process_local_vision(self, prompt, images):
        """Traitement des images via Ollama en Local (LLaVA) - Ton code original"""
        payload = {
            "model": self.vision_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "images": images,
            "options": {
                "temperature": 0.0,
                "num_ctx": 4096,
                "num_predict": 1000
            }
        }
        try:
            response = requests.post(self.api_url, json=payload, timeout=500) 
            if response.status_code == 200:
                json_resp = response.json()
                return ResponseWrapper(json_resp.get("response", ""))
            else:
                return ResponseWrapper(f'{{"error": "Erreur Ollama {response.status_code}"}}')
        except Exception as e:
            st.toast(f"🚨 Vérifiez que 'ollama run {self.vision_model}' tourne en arrière-plan !", icon="🛑")
            return ResponseWrapper('{"nom": "Erreur Connexion", "reasoning": "Modèle LLaVA introuvable ?"}')

    def _image_to_base64(self, image):
        try:
            buf = BytesIO()
            if image.mode in ("RGBA", "P"): image = image.convert("RGB")
            image.save(buf, format="JPEG", quality=85) 
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        except:
            return None

    @property
    def client(self): return self

def create_analyzer():
    return LLMAnalyzer()