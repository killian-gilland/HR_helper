# Fichier : src/modules/scoring_engine.py
import json
import re
from src.modules.llm_analyzer import create_analyzer

def process_cv_scoring(text_content, job_desc) -> dict:
    """Analyse le CV et applique un coupe-circuit Python strict pour les hors-sujets."""
    llm = create_analyzer()
    prompt = f"""
    Tu es un Lead Tech et un Recruteur d'Élite. Ton but est d'évaluer l'adéquation d'un candidat.
    
    OFFRE D'EMPLOI : {job_desc[:1500]}
    CV DU CANDIDAT : {text_content[:6000]}
    
    🚨 ÉTAPE 1 : LE FILTRE ÉLIMINATOIRE
    Analyse si le métier actuel et l'expérience du candidat ont un lien avec l'offre. 
    Exemple de hors-sujet : Un commercial, boulanger, ou manager non-technique qui postule pour un poste d'ingénieur/Data Scientist.
    Si le profil est hors-sujet, définis STRICTEMENT la clé "est_hors_sujet" à true. Sinon, false.
    
    ÉTAPE 2 : SCORING (Uniquement si le profil est pertinent)
    - 'n_hard_skills_coeur' (Sur 65) :
       * 55-65 : Expertise Totale.
       * 45-54 : Opérationnel Solide.
       * 30-44 : Fondations / Profil Junior.
       * 15-29 : Syndrome du Mot-Clé / Superficiel.
       * 0-14 : Très insuffisant.
    - 'n_outils_metier' (Sur 10) : Pratique de l'écosystème.
    - 'n_business_impact' (Sur 10) : Chiffrage de l'impact (ex: "X€", "X%").
    - 'n_seniorite' (Sur 5) : Cohérence avec le poste.
    - 'n_soft_skills' (Sur 5) : Rigueur, clarté.
    - 'n_storytelling' (Sur 5) : Explication du "pourquoi/comment".
    
    OUTPUT JSON STRICT : 
    IMPORTANT : La clé "est_hors_sujet" DOIT être la toute première.
    {{ 
        "est_hors_sujet": true,
        "enjeu_offre": "Le besoin principal de cette offre est...",
        "preuve_ingenierie": "Le candidat montre [une forte / moyenne / faible] capacité...",
        "niveau_bullshit": "Faible/Élevé/Hors-Sujet.",
        "nom": "Prénom Nom",
        "titre_profil": "Titre du profil sur le CV",
        "email": "email@trouvé_ou_vide",
        "années_exp": 0,
        "compétences": ["C1", "C2"],
        "réalisations_clés": ["Action 1"],
        "n_hard_skills_coeur": 0, 
        "n_outils_metier": 0, 
        "n_business_impact": 0,
        "n_seniorite": 0, 
        "n_soft_skills": 0, 
        "n_storytelling": 0,
        "strength": "Sa plus grande force", 
        "risk": "Le point de vigilance", 
        "reasoning": "Conclusion cash" 
    }}
    """
    try:
        response = llm.client.generate_content(prompt)
        txt = response.text
        json_match = re.search(r'\{.*\}', txt, re.DOTALL)
        if json_match: 
            data = json.loads(json_match.group(0))
            
            # ⚡ LE COUPE-CIRCUIT PYTHON (ANTI-HALLUCINATION) ⚡
            # Si l'IA a détecté un hors-sujet, on écrase manuellement ses notes fantaisistes
            if data.get("est_hors_sujet") is True or data.get("est_hors_sujet") == "true":
                data["n_hard_skills_coeur"] = 0
                data["n_outils_metier"] = 0
                data["n_business_impact"] = 0
                data["n_seniorite"] = 0
                data["n_soft_skills"] = 0
                data["n_storytelling"] = 0
                data["score_final"] = 0
                data["strength"] = "Aucune"
                data["risk"] = "HORS-SUJET TOTAL"
                data["reasoning"] = "❌ REJET AUTOMATIQUE : Le background du candidat ne correspond pas au métier de l'offre."
                
            return data
        return {"nom": "Erreur JSON"}
    except Exception as e: return {"nom": f"Erreur IA : {str(e)}"}