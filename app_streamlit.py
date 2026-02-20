"""
Recruitment Analyst - ÉDITION UNIVERSELLE (50% Cœur de Métier) + SÉCURITÉ ANTI-HALLUCINATION
Moteur de scoring agnostique avec bridage strict des notes par Python.
"""
import streamlit as st
import pandas as pd
import json
import logging
import os
import sys
import re

st.set_page_config(page_title="🦙 AI Recruiter", page_icon="🌍", layout="wide")

if "df_candidates" not in st.session_state:
    st.session_state.df_candidates = None

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from src.modules.llm_analyzer import create_analyzer
    from src.modules.pdf_utils import extract_text_from_pdf
except ImportError:
    st.error("Erreur d'import. Vérifiez vos dossiers.")
    st.stop()

logging.basicConfig(level=logging.INFO)

# ==================== LOGIQUE MÉTIER ====================

def _extract_data_from_cv(text_content) -> dict:
    llm = create_analyzer()
    prompt = f"""
    Tu es un recruteur expert. Analyse ce CV et extrais les données en JSON STRICT. NE TRADUIS PAS LES CLÉS.
    
    RÈGLES IMPÉRATIVES :
    1. 'titre_profil' : Donne le métier actuel ou le titre principal du CV.
    2. 'années_exp' : CALCULE le nombre total d'années d'expérience. Renvoie un CHIFFRE ENTIER.
    3. 'compétences' : Isole les 5 mots-clés techniques ou métiers principaux.
    4. 'réalisations_clés' : Résume les 3 accomplissements majeurs (8 MOTS MAX).
    5. 'ecole' : Identifie l'école du plus haut diplôme.
    6. 'ligue' : 'A' = Top 100 Mondial / Écoles d'élite. 'B' = Bonnes universités / Écoles classiques. 'C' = Lycées, BTS, IUT, inconnu.
    
    ATTENTION : LE JSON CI-DESSOUS EST JUSTE UN SQUELETTE.
    
    FORMAT ATTENDU :
    {{
        "nom": "Prénom Nom",
        "titre_profil": "Titre",
        "email": "email",
        "années_exp": 0,
        "compétences": ["Mot1", "Mot2"],
        "réalisations_clés": ["Action 1", "Action 2"],
        "ecole": "Nom de l'école",
        "ligue": "C"
    }}
    
    TEXTE DU CV :
    {text_content[:6000]}
    """
    try:
        response = llm.client.generate_content(prompt)
        txt = response.text
        json_match = re.search(r'\{.*\}', txt, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return {
                "nom": data.get("nom", "Inconnu"),
                "titre_profil": data.get("titre_profil", "Non précisé"),
                "email": data.get("email", "N/A"),
                "années_exp": data.get("années_exp", 0),
                "compétences": data.get("compétences", []),
                "réalisations_clés": data.get("réalisations_clés", []),
                "ecole": data.get("ecole", "Non renseignée"),
                "ligue": data.get("ligue", "C")
            }
        return {"nom": "Erreur JSON"}
    except: return {"nom": "Erreur IA"}

def _evaluate_candidate_qualitative(candidate_data, job_desc):
    llm = create_analyzer()
    safe_data = {k: v for k, v in candidate_data.items() if k not in ["ecole", "ligue"]}
    cv_txt = json.dumps(safe_data, ensure_ascii=False)
    
    prompt = f"""
    Tu es un Directeur du Recrutement Expert (Tous secteurs confondus). Ton but est d'évaluer l'adéquation exacte entre ce candidat et l'offre.
    La COMPÉTENCE CŒUR DU MÉTIER (Hard Skills fondamentales) est reine et vaut 50% de la note.
    
    JOB DESCRIPTION: {job_desc[:1500]}
    CANDIDAT: {cv_txt}
    
    TACHE : Évalue ce profil sur 8 critères universels (Total 100 points).
    
    BARÈME STRICT :
    - 'n_hard_skills_coeur' (Sur 50) : Maîtrise absolue des fondations du métier demandé (ex: Négociation pour un commercial, Code pour un dev, Paie pour un RH). 0 si totalement hors-sujet.
    - 'n_outils_metier' (Sur 10) : Maîtrise des logiciels/outils périphériques (ex: CRM, ERP, Git, Excel).
    - 'n_business_impact' (Sur 10) : Preuves de réussite (CA généré, litiges résolus, temps gagné).
    - 'n_seniorite' (Sur 10) : Adéquation du nombre d'années d'expérience.
    - 'n_envergure' (Sur 5) : Complexité des projets, taille des budgets ou des équipes gérées.
    - 'n_secteur' (Sur 5) : 5 si même industrie. 0 si le secteur n'a AUCUN rapport.
    - 'n_soft_skills' (Sur 5) : Preuves de leadership, communication, esprit d'équipe.
    - 'n_storytelling' (Sur 5) : Clarté du CV, progression logique de carrière.
    
    ATTENTION : REMPLACE LES ZÉROS DU SQUELETTE PAR TES VRAIES NOTES. N'utilise pas que des notes parfaites.
    
    OUTPUT JSON STRICT: 
    {{ 
        "n_hard_skills_coeur": 0,
        "n_outils_metier": 0,
        "n_business_impact": 0,
        "n_seniorite": 0,
        "n_envergure": 0,
        "n_secteur": 0,
        "n_soft_skills": 0,
        "n_storytelling": 0,
        "strength": "Atout majeur prouvé", 
        "risk": "Lacune métier précise", 
        "reasoning": "Une phrase courte expliquant la note principale" 
    }}
    """
    try:
        res = llm.client.generate_content(prompt)
        txt = res.text
        start = txt.find("{")
        end = txt.rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(txt[start:end])
        return {}
    except: return {}

# ==================== INTERFACE ====================

st.title("🌍 AI Recruiter : Universel & Sécurisé")
st.info("Algorithme Agnostique : Les compétences fondamentales du métier (Hard Skills) pèsent 50% de la note. Les notes sont strictement bridées par Python pour éviter les hallucinations.")

with st.sidebar:
    st.header("1. Import des CVs (PDF)")
    uploaded_files = st.file_uploader("Fichiers PDF", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files and st.button("🚀 Extraire les Profils"):
        parsed_data = []
        bar = st.progress(0)
        
        for i, file in enumerate(uploaded_files):
            text = extract_text_from_pdf(file)
            if not text or len(text) < 20 or "ERREUR" in text:
                parsed_data.append({"nom": "Fichier Vide/Scan", "ligue": "C"})
            else:
                parsed_data.append(_extract_data_from_cv(text))
            bar.progress((i + 1) / len(uploaded_files))
            
        st.session_state.df_candidates = pd.DataFrame(parsed_data)
        st.success("Extraction terminée !")

    st.divider()
    st.header("2. Fiche de Poste")
    job_description = st.text_area("Description du Job", height=150)

if st.session_state.df_candidates is not None and not st.session_state.df_candidates.empty:
    st.subheader("📋 Analyse des Profils et Ligues")
    
    display_df = st.session_state.df_candidates.copy()
    if "compétences" in display_df.columns:
        display_df["compétences"] = display_df["compétences"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
    if "réalisations_clés" in display_df.columns:
        display_df["réalisations_clés"] = display_df["réalisations_clés"].apply(lambda x: " • " + "\n• ".join(x) if isinstance(x, list) and x else "Aucune")
    
    cols = display_df.columns.tolist()
    if 'titre_profil' in cols:
        cols.insert(1, cols.pop(cols.index('titre_profil')))
        display_df = display_df[cols]
        
    st.dataframe(display_df, use_container_width=True)
    
    if job_description and st.button("⭐ Lancer le Scoring Universel"):
        candidates = st.session_state.df_candidates.to_dict('records')
        results = []
        eval_bar = st.progress(0)
        
        for i, cand in enumerate(candidates):
            if cand.get("nom") == "Fichier Vide/Scan":
                cand.update({"score_final": 0, "reasoning": "Fichier non lu"})
                results.append(cand)
                continue
                
            eval_data = _evaluate_candidate_qualitative(cand, job_description)
            
            # --- LE PARSEUR ANTI-HALLUCINATION (LIMITES STRICTES) ---
            n_coeur = min(int(eval_data.get("n_hard_skills_coeur", 0)), 50)
            n_outils = min(int(eval_data.get("n_outils_metier", 0)), 10)
            n_imp = min(int(eval_data.get("n_business_impact", 0)), 10)
            n_sen = min(int(eval_data.get("n_seniorite", 0)), 10)
            n_env = min(int(eval_data.get("n_envergure", 0)), 5)
            n_sect = min(int(eval_data.get("n_secteur", 0)), 5)
            n_soft = min(int(eval_data.get("n_soft_skills", 0)), 5)
            n_story = min(int(eval_data.get("n_storytelling", 0)), 5)
            
            base_score = n_coeur + n_outils + n_imp + n_sen + n_env + n_sect + n_soft + n_story
            
            details = (f"🎯 Compétence Cœur: {n_coeur}/50 | 🛠️ Outils: {n_outils}/10 | 📈 Impact: {n_imp}/10 | "
                       f"⏳ Séniorité: {n_sen}/10 | 🧩 Envergure: {n_env}/5 | 🏢 Secteur: {n_sect}/5 | "
                       f"🤝 Soft Skills: {n_soft}/5 | 📖 Storytelling: {n_story}/5")
            
            ligue = str(cand.get("ligue", "C")).upper()
            bonus = 15 if "A" in ligue else (5 if "B" in ligue else 0)
            
            final_score = min(base_score + bonus, 100)
            
            cand.update({
                "score_final": final_score,
                "score_base": base_score,
                "bonus_ecole": bonus,
                "details_score": details,
                "strength": eval_data.get("strength", ""),
                "risk": eval_data.get("risk", ""),
                "reasoning": eval_data.get("reasoning", "")
            })
            results.append(cand)
            eval_bar.progress((i + 1) / len(candidates))
        
        results.sort(key=lambda x: int(x.get('score_final', 0)), reverse=True)
        st.divider()
        st.subheader("🏆 Classement Final Universel")
        
        for res in results:
            with st.container():
                c1, c2 = st.columns([1, 4])
                
                c1.metric(
                    label="Score Global", 
                    value=f"{res.get('score_final', 0)}/100", 
                    delta=f"+{res.get('bonus_ecole', 0)} pts (Ligue {res.get('ligue', 'C')})"
                )
                
                c2.markdown(f"### {res.get('nom', 'Inconnu')} - {res.get('titre_profil', '')} ({res.get('années_exp', 0)} ans d'exp)")
                c2.markdown(f"🎓 **{res.get('ecole', 'École non précisée')}** — *Ligue {res.get('ligue', 'C')}*")
                c2.markdown(f"📊 **Détail du Score Base ({res.get('score_base', 0)}/100) :**\n{res.get('details_score', '')}")
                c2.markdown(f"**Analyse :** {res.get('reasoning', '')}")
                c2.success(f"💪 **Force:** {res.get('strength', '')}")
                c2.error(f"⚠️ **Risque:** {res.get('risk', '')}")
                st.divider()