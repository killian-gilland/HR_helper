"""
Recruitment Analyst - HYBRID SNIPER EDITION (PDF Standard)
Extrait des données chirurgicales : calcul d'expérience, mots-clés, et actions ultra-courtes.
"""
import streamlit as st
import pandas as pd
import json
import logging
import os
import sys
import re

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="🦙 AI Recruiter", page_icon="🎯", layout="wide")

if "df_candidates" not in st.session_state:
    st.session_state.df_candidates = None

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from src.modules.llm_analyzer import create_analyzer
    from src.modules.pdf_utils import extract_text_from_pdf
except ImportError:
    st.error("Erreur d'import. Vérifiez vos dossiers et que vous lancez depuis la racine.")
    st.stop()

logging.basicConfig(level=logging.INFO)

# ==================== LOGIQUE MÉTIER ====================

def _extract_data_from_cv(text_content) -> dict:
    """Extrait les réalisations concrètes avec le prompt ultra-strict."""
    llm = create_analyzer()
    
    # LE PROMPT "SNIPER" EST ICI :
    prompt = f"""
    Tu es un recruteur expert. Analyse ce CV et extrais les données en JSON STRICT. NE TRADUIS PAS LES CLÉS.
    
    RÈGLES IMPÉRATIVES :
    1. 'années_exp' : CALCULE le nombre total d'années d'expérience en lisant les dates (ex: 2022-2026 = 4). Renvoie un CHIFFRE ENTIER.
    2. 'compétences' : Isole les 5 mots-clés techniques ou soft-skills principaux.
    3. 'réalisations_clés' : Résume les 3 plus grands accomplissements. MAXIMUM 8 MOTS par réalisation. Commence par un verbe d'action. Pas de blabla.
    
    FORMAT ATTENDU :
    {{
        "nom": "Prénom Nom",
        "email": "email",
        "années_exp": 4,
        "compétences": ["Mot1", "Mot2", "Mot3"],
        "réalisations_clés": ["Créé un modèle prédictif", "Automatisé les processus RGPD"]
    }}
    
    TEXTE DU CV :
    {text_content[:6000]}
    """
    
    try:
        # Debug Terminal
        print("\n" + "▼"*60)
        print(f"🔍 CE QUE PYTHON A LU DU PDF (Extrait) :\n{text_content[:600]}...\n")
        
        response = llm.client.generate_content(prompt)
        txt = response.text
        
        print(f"🤖 RÉPONSE BRUTE DE L'IA :\n{txt}")
        print("▲"*60 + "\n")

        json_match = re.search(r'\{.*\}', txt, re.DOTALL)
        
        if json_match:
            data = json.loads(json_match.group(0))
            return {
                "nom": data.get("nom", data.get("Name", data.get("Nom", "Inconnu"))),
                "email": data.get("email", data.get("Email", "N/A")),
                "années_exp": data.get("années_exp", data.get("Experience", 0)),
                "compétences": data.get("compétences", data.get("Skills", [])),
                "réalisations_clés": data.get("réalisations_clés", data.get("Achievements", []))
            }
        else:
            return {"nom": "Erreur JSON", "compétences": [], "réalisations_clés": ["L'IA n'a pas formaté en JSON."]}
            
    except Exception as e:
        return {"nom": "Erreur IA", "compétences": [], "réalisations_clés": [str(e)[:50]]}

def _evaluate_candidate_qualitative(candidate_data, job_desc):
    """Évalue le candidat de manière synthétique."""
    llm = create_analyzer()
    cv_txt = json.dumps(candidate_data, ensure_ascii=False)
    
    prompt = f"""
    JOB DESCRIPTION: {job_desc[:1500]}
    CANDIDAT : {cv_txt}
    
    TACHE: Évalue la capacité de ce candidat à réussir dans ce poste selon son profil strict.
    
    OUTPUT JSON STRICT: 
    {{ 
        "score": 0, 
        "strength": "Son plus grand atout", 
        "risk": "Ce qui manque", 
        "reasoning": "Explication courte de la note" 
    }}
    """
    try:
        res = llm.client.generate_content(prompt)
        txt = res.text
        start = txt.find("{")
        end = txt.rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(txt[start:end])
        return {"score": 0}
    except: return {"score": 0}

# ==================== INTERFACE ====================

st.title("🎯 AI Recruiter : Mode Hybride Sniper")
st.info("L'IA est désormais bridée : elle calcule l'expérience, sort des mots-clés, et résume les actions en 8 mots max.")

with st.sidebar:
    st.header("1. Import des CVs (PDF)")
    uploaded_files = st.file_uploader("Fichiers PDF", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files and st.button("🚀 Extraire les Profils"):
        parsed_data = []
        bar = st.progress(0)
        
        for i, file in enumerate(uploaded_files):
            text_content = extract_text_from_pdf(file)

            if not text_content or len(text_content) < 20 or "ERREUR" in text_content:
                extracted_json = {
                    "nom": "Fichier Vide/Scan", 
                    "email": "N/A",
                    "années_exp": 0,
                    "compétences": [],
                    "réalisations_clés": ["Le PDF est illisible."]
                }
            else:
                extracted_json = _extract_data_from_cv(text_content)

            # Formatage propre pour le tableau
            safe_data = {
                "nom": extracted_json.get("nom", "Inconnu"),
                "email": extracted_json.get("email", "N/A"),
                "années_exp": extracted_json.get("années_exp", 0),
                "compétences": ", ".join(extracted_json.get("compétences", [])) if extracted_json.get("compétences") else "N/A",
                "réalisations_clés": " • " + "\n• ".join(
                    extracted_json.get("réalisations_clés", [])
                ) if extracted_json.get("réalisations_clés") else "Aucune action identifiée"
            }
            parsed_data.append(safe_data)
            bar.progress((i + 1) / len(uploaded_files))
            
        st.session_state.df_candidates = pd.DataFrame(parsed_data)
        st.success("Extraction terminée !")

    st.divider()
    st.header("2. Fiche de Poste")
    job_description = st.text_area("Description du Job", height=150)

# --- VISUALISATION ---

if st.session_state.df_candidates is not None and not st.session_state.df_candidates.empty:
    st.subheader("📋 Analyse Synthétique")
    st.dataframe(st.session_state.df_candidates, use_container_width=True)
    
    if job_description and st.button("⭐ Noter les Candidats"):
        candidates = st.session_state.df_candidates.to_dict('records')
        results = []
        eval_bar = st.progress(0)
        
        for i, cand in enumerate(candidates):
            if cand.get("nom") == "Fichier Vide/Scan":
                cand.update({"score": 0, "reasoning": "Fichier non lu"})
                results.append(cand)
            else:
                eval_data = _evaluate_candidate_qualitative(cand, job_description)
                cand.update(eval_data)
                results.append(cand)
            
            eval_bar.progress((i + 1) / len(candidates))
        
        # Tri et Affichage
        results.sort(key=lambda x: int(x.get('score', 0)), reverse=True)
        st.divider()
        st.subheader("🏆 Classement Final")
        
        for res in results:
            with st.container():
                c1, c2 = st.columns([1, 4])
                score = res.get('score', 0)
                
                c1.metric("Score", f"{score}/100")
                c2.markdown(f"**{res['nom']}** ({res['années_exp']} ans d'exp)")
                c2.markdown(f"**Analyse:** {res.get('reasoning', '')}")
                c2.success(f"💪 **Force:** {res.get('strength', '')}")
                c2.error(f"⚠️ **Risque:** {res.get('risk', '')}")
                st.divider()