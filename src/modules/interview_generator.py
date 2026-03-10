# Fichier : src/modules/interview_generator.py
import json
import re
from src.modules.llm_analyzer import create_analyzer

def generate_interview_questions(candidate_data: dict, job_desc: str) -> dict:
    """Génère des questions d'entretien ciblées basées sur l'analyse du CV."""
    llm = create_analyzer()
    prompt = f"""
    Tu es un Lead Tech préparant un entretien d'embauche décisif.
    Voici l'analyse IA du CV de ce candidat :
    - Sa plus grande force : {candidate_data.get('strength')}
    - Son point de vigilance/risque : {candidate_data.get('risk')}
    - Synthèse : {candidate_data.get('reasoning')}
    
    OFFRE D'EMPLOI : {job_desc[:1500]}
    
    Génère 3 questions d'entretien redoutables et très précises pour ce candidat.
    
    OUTPUT JSON STRICT : 
    {{ 
        "q1_force": {{
            "titre": "💪 Vérification de la force",
            "question": "Votre question technique ici...",
            "attente": "Ce qu'il faut écouter dans sa réponse pour valider qu'il ne ment pas..."
        }},
        "q2_risque": {{
            "titre": "⚠️ Creuser la lacune",
            "question": "Votre question ici...",
            "attente": "Ce qu'il faut écouter pour s'assurer que ce risque n'est pas bloquant..."
        }},
        "q3_situation": {{
            "titre": "🎯 Mise en situation métier",
            "question": "Votre question de mise en situation liée à l'offre...",
            "attente": "L'approche ou le réflexe que le candidat doit démontrer..."
        }}
    }}
    """
    try:
        response = llm.client.generate_content(prompt)
        txt = response.text
        json_match = re.search(r'\{.*\}', txt, re.DOTALL)
        if json_match: 
            return json.loads(json_match.group(0))
        return {}
    except Exception as e: 
        return {}