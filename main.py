from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import uvicorn
import sys
import os

# --- Ajout du dossier courant pour les imports ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- Import de tes modules existants (Rien ne change ici !) ---
from src.modules.utils import extract_text_from_pdf
from src.modules.db_manager import (init_db, create_user, verify_user, create_job_offer, 
                                    get_all_job_offers, save_candidate, get_candidates_by_offer, 
                                    delete_candidate, delete_job_offer, update_candidate_data)
from src.modules.scoring_engine import process_cv_scoring
from src.modules.interview_generator import generate_interview_questions

# Initialisation de la base
init_db()

# Création de l'API
app = FastAPI(title="Talent AI Backend")

# ⚡ TRÈS IMPORTANT : Autoriser React à parler avec Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En production, on mettra l'URL exacte de ton React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODÈLES DE DONNÉES ---
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    company: str
    username: str
    password: str

class OfferRequest(BaseModel):
    title: str
    description: str
    user_id: int

# ==================== ROUTES DE L'API ====================

@app.post("/api/auth/login")
def login(request: LoginRequest):
    user = verify_user(request.username, request.password)
    if user:
        return {"logged_in": True, "user_id": user[0], "company_name": user[1]}
    raise HTTPException(status_code=401, detail="Identifiants incorrects")

@app.post("/api/auth/register")
def register(request: RegisterRequest):
    success = create_user(request.username, request.password, request.company)
    if success:
        return {"success": True}
    raise HTTPException(status_code=400, detail="L'utilisateur existe déjà")

@app.get("/api/offers/{user_id}")
def get_offers(user_id: int):
    df = get_all_job_offers(user_id)
    return df.to_dict(orient="records")

@app.post("/api/offers")
def create_offer(request: OfferRequest):
    offer_id = create_job_offer(request.title, request.description, request.user_id)
    return {"offer_id": offer_id}

@app.delete("/api/offers/{offer_id}")
def delete_offer(offer_id: int):
    delete_job_offer(offer_id)
    return {"success": True}

@app.get("/api/candidates/{offer_id}")
def get_candidates(offer_id: int):
    df = get_candidates_by_offer(offer_id)
    return df.to_dict(orient="records")

@app.delete("/api/candidates/{candidate_id}")
def delete_cand(candidate_id: int):
    delete_candidate(candidate_id)
    return {"success": True}

@app.post("/api/scan")
async def scan_cvs(offer_id: int = Form(...), description: str = Form(...), files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        # On lit le contenu du PDF envoyé par React
        content = await file.read()
        
        # NOTE: Tu devras peut-être adapter `extract_text_from_pdf` pour qu'il lise des bytes au lieu d'un fichier physique
        # text = extract_text_from_pdf(content) 
        text = "Texte factice pour le test de connexion API" # A REMPLACER par ton vrai extracteur
        
        if len(text) > 20:
            data = process_cv_scoring(text, description)
            data["score_final"] = min(int(data.get("n_hard_skills_coeur",0)), 65) + min(int(data.get("n_outils_metier",0)), 10)
            save_candidate(data, offer_id)
            results.append({"filename": file.filename, "status": "success", "score": data["score_final"]})
        else:
            save_candidate({"nom": file.filename, "score_final": 0, "reasoning": "Erreur de lecture"}, offer_id)
            results.append({"filename": file.filename, "status": "error"})
            
    return {"results": results}

# --- Lancement du serveur ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)