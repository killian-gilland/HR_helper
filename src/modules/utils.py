"""
PDF Utils : Lecture Texte Uniquement (Clean Version)
"""
import pypdf
import logging
import pandas as pd
import json

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


def prepare_export_df(df_history, lang='fr'):
    if df_history.empty:
        return pd.DataFrame()
        
    export_list = []
    for idx, row in df_history.iterrows():
        try:
            data = json.loads(row['analyse_json'])
        except:
            data = {}
            
        q_data = data.get("interview_questions", {})
        
        if lang == 'en':
            export_list.append({
                "Date": row['date_scan'], 
                "Candidate Name": row['nom'], 
                "Profile Title": row['titre_profil'],
                "Global Score": row['score_final'], 
                "Tech Core": data.get("n_coeur", 0),
                "Tools": data.get("n_outils", 0), 
                "Business Impact": data.get("n_imp", 0),
                "Seniority": data.get("n_sen", 0), 
                "Soft Skills": data.get("n_soft", 0),
                "Strength": data.get("strength", ""), 
                "Risk": data.get("risk", ""), 
                "AI Conclusion": data.get("reasoning", ""),
                "Question 1 (Strength)": q_data.get("q1_force", {}).get("question", "Not generated"),
                "Question 2 (Risk)": q_data.get("q2_risque", {}).get("question", "Not generated"),
                "Question 3 (Situation)": q_data.get("q3_situation", {}).get("question", "Not generated")
            })
        else:
            export_list.append({
                "Date d'analyse": row['date_scan'], 
                "Nom du candidat": row['nom'], 
                "Titre Profil": row['titre_profil'],
                "Score Global (/100)": row['score_final'], 
                "Cœur Tech (/65)": data.get("n_coeur", 0),
                "Outils (/10)": data.get("n_outils", 0), 
                "Impact Business (/10)": data.get("n_imp", 0),
                "Séniorité (/5)": data.get("n_sen", 0), 
                "Soft Skills (/5)": data.get("n_soft", 0),
                "Atout Principal": data.get("strength", ""), 
                "Point de Vigilance (Risque)": data.get("risk", ""), 
                "Conclusion IA": data.get("reasoning", ""),
                "Question 1 (Valider la force)": q_data.get("q1_force", {}).get("question", "Non générée"),
                "Question 2 (Creuser le risque)": q_data.get("q2_risque", {}).get("question", "Non générée"),
                "Question 3 (Mise en situation)": q_data.get("q3_situation", {}).get("question", "Non générée")
            })
            
    return pd.DataFrame(export_list)