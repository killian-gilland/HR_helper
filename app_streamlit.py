"""
Recruitment Analyst - ÉDITION DASHBOARD ENTERPRISE
Architecture Modulaire (src/modules/), UI/UX SaaS B2B, et Scoring Strict mais Nuancé.
"""
import streamlit as st
import pandas as pd
import json
import logging
import os
import sys
import re
import time
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Talent AI | Enterprise Sourcing", page_icon="🧿", layout="wide", initial_sidebar_state="expanded")

# --- INJECTION CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {font-family: 'Inter', sans-serif !important;}
    .stApp {background-color: #F8FAFC !important;}
    #MainMenu, header, footer {display: none !important;}
    .block-container {padding-top: 1.5rem !important; max-width: 1400px !important;}
    
    /* --- SIDEBAR CUSTOMIZATION --- */
    [data-testid="stSidebar"] {
        background-color: #0B1120 !important;
        border-right: 1px solid #1E293B !important;
    }
    
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {
        color: #F8FAFC !important;
    }
    
    /* =========================================
       🧨 CORRECTIF NUCLÉAIRE 1 : L'OFFRE D'EMPLOI
       ========================================= */
    [data-testid="stSidebar"] .stTextArea textarea {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] .stTextArea textarea:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 1px #3B82F6 !important;
    }
    [data-testid="stSidebar"] .stTextArea label { display: none !important; }

    /* =========================================
       🧨 CORRECTIF NUCLÉAIRE 2 : LA ZONE DE DÉPÔT CV
       ========================================= */
    [data-testid="stFileUploadDropzone"] {
        background-color: #0F172A !important;
        border: 2px dashed #475569 !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploadDropzone"] *, 
    [data-testid="stFileUploadDropzone"] span, 
    [data-testid="stFileUploadDropzone"] small, 
    [data-testid="stFileUploadDropzone"] svg {
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
        fill: #F8FAFC !important;
    }
    
    [data-testid="stFileUploader"] button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: #2563EB !important;
    }
    
    /* Bouton Principal de Scan */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        border: 1px solid #1E40AF !important;
        padding: 0.8rem 0 !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: transform 0.2s;
    }
    
    /* --- MAIN DASHBOARD CARDS --- */
    .dash-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #E2E8F0;
        height: 100%;
    }
    
    .spotlight-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
        border: 2px solid #3B82F6;
        position: relative;
        overflow: hidden;
    }
    
    .meter-container {
        background: #E2E8F0;
        border-radius: 4px;
        height: 8px;
        width: 100%;
        margin-top: 4px;
        margin-bottom: 12px;
        overflow: hidden;
    }
    .meter-fill { height: 100%; border-radius: 4px; }
    
    .badge-tech {
        background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE;
        padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; margin: 2px; display: inline-block;
    }
    
    [data-testid="stExpander"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        background: #F8FAFC !important;
        margin-bottom: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- IMPORTS PROPRES (Architecture Modulaire) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.modules.llm_analyzer import create_analyzer
    from src.modules.pdf_utils import extract_text_from_pdf
except ImportError as e:
    st.error(f"Erreur d'import : {e}. Assurez-vous que les dossiers 'src' et 'modules' contiennent bien des fichiers __init__.py")
    st.stop()

logging.basicConfig(level=logging.INFO)

# ==================== LOGIQUE MÉTIER ====================
# ==================== LOGIQUE MÉTIER ====================
# ==================== LOGIQUE MÉTIER ====================
def _process_cv_one_shot(text_content, job_desc) -> dict:
    llm = create_analyzer()
    prompt = f"""
    Tu es un Directeur d'Ingénierie (VP of Engineering) extrêmement exigeant.
    Ton but : recruter des "Problem Solvers" qui comprennent le produit, pas des "Dictionnaires de mots-clés".
    
    OFFRE D'EMPLOI : {job_desc[:1500]}
    CV DU CANDIDAT : {text_content[:6000]}
    
    RÈGLES D'ÉVALUATION DRASTIQUES (CHANGEMENT DE PARADIGME) :
    Tu vas évaluer la CAPACITÉ À RÉSOUDRE LE PROBLÈME CENTRAL DE L'OFFRE, pas faire un jeu de correspondances de mots.
    
    - 'n_hard_skills_coeur' (Sur 65) - ÉVALUATION DE L'INGÉNIERIE ET DU CONTEXTE :
       * 50 à 65 : Le candidat prouve qu'il a déjà résolu LES MÊMES DÉFIS que l'offre (ex: scalabilité, refonte, création from scratch), avec un niveau de complexité similaire. Peu importe s'il lui manque un outil mineur, c'est un vrai ingénieur.
       * 30 à 49 : Le candidat a le bon socle technique, mais les contextes de ses projets passés sont un peu plus simples ou différents de l'offre.
       * 10 à 29 : SYNDROME DU MOT-CLÉ. Le CV est un catalogue de technos sans contexte. Tu ne comprends pas ce qu'il a vraiment construit ni pourquoi. LA NOTE NE DOIT PAS DÉPASSER 29, même si toutes les technos de l'offre sont écrites sur le CV.
       * 0 à 9 : Aucun rapport avec l'ingénierie demandée.
       
    - 'n_outils_metier' (Sur 10) : Pratique des bons paradigmes (ex: CI/CD, Cloud, tests automatisés) plus que des outils précis.
    - 'n_business_impact' (Sur 10) : 0 s'il n'y a que des descriptions de tâches génériques.
    - 'n_seniorite' (Sur 5) : Cohérence de l'expérience avec la difficulté du poste.
    - 'n_soft_skills' (Sur 5) : Rigueur, clarté.
    - 'n_storytelling' (Sur 5) : 0 si c'est un CV "liste de courses".
    
    OUTPUT JSON STRICT : 
    IMPORTANT : Remplis d'abord "enjeu_offre", "preuve_ingenierie" et "niveau_bullshit". C'est ce qui va forcer ta note finale à changer DRASTIQUEMENT.
    {{ 
        "enjeu_offre": "L'enjeu numéro 1 du poste n'est pas d'utiliser [Techno], c'est de [ex: scaler une API, maintenir du legacy, construire from scratch]...",
        "preuve_ingenierie": "Le candidat a-t-il prouvé qu'il a déjà géré cet enjeu précis ? Oui/Non, car...",
        "niveau_bullshit": "[Faible/Élevé]. Le CV explique [bien le 'pourquoi' et le 'comment' / ou est juste une liste de technos balancées au hasard].",
        "nom": "Prénom Nom",
        "titre_profil": "Titre du profil sur le CV",
        "email": "email@trouvé_ou_vide",
        "années_exp": 0,
        "compétences": ["C1", "C2", "C3"],
        "réalisations_clés": ["Action 1", "Action 2"],
        "n_hard_skills_coeur": 0, 
        "n_outils_metier": 0, 
        "n_business_impact": 0,
        "n_seniorite": 0, 
        "n_soft_skills": 0, 
        "n_storytelling": 0,
        "strength": "Sa plus grande preuve d'ingénierie concrète", 
        "risk": "Le plus grand décalage avec la réalité du poste", 
        "reasoning": "Conclusion cash et directe" 
    }}
    """
    try:
        response = llm.client.generate_content(prompt)
        txt = response.text
        json_match = re.search(r'\{.*\}', txt, re.DOTALL)
        if json_match: return json.loads(json_match.group(0))
        return {"nom": "Erreur JSON"}
    except Exception as e: return {"nom": f"Erreur IA : {str(e)}"}

def create_radar_chart(res):
    categories = ['Cœur Tech', 'Outils', 'Impact', 'Séniorité', 'Soft Skills', 'Clarté/Récit']
    values = [
        (res.get('n_coeur', 0) / 65) * 100, (res.get('n_outils', 0) / 10) * 100,
        (res.get('n_imp', 0) / 10) * 100, (res.get('n_sen', 0) / 5) * 100,
        (res.get('n_soft', 0) / 5) * 100, (res.get('n_story', 0) / 5) * 100
    ]
    values.append(values[0])
    categories_closed = categories + [categories[0]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories_closed, fill='toself', fillcolor='rgba(59, 130, 246, 0.2)',
        line=dict(color='#3B82F6', width=2), name=res.get('nom', 'Candidat')
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)),
        showlegend=False, margin=dict(l=30, r=30, t=20, b=20), height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def make_progress_bar(label, value, max_val, color_hex="#3B82F6"):
    percent = (value / max_val) * 100
    return f"""
    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600; color: #475569; margin-top: 6px;">
        <span>{label}</span><span>{value}/{max_val}</span>
    </div>
    <div class="meter-container"><div class="meter-fill" style="width: {percent}%; background-color: {color_hex};"></div></div>
    """

# ==================== INTERFACE SAAS ====================
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 900; font-size: 1.8rem; margin-bottom: 0;'>🧿 TALENT<span style='color: #3B82F6;'>.AI</span></h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 0.75rem; font-weight: 600; margin-top: 0; margin-bottom: 30px; letter-spacing: 1px;'>ENTERPRISE SOURCING ENGINE</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 5px;'>1. Base de CV (PDF)</p>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    st.markdown("<br><p style='font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 5px;'>2. Job Description</p>", unsafe_allow_html=True)
    job_description = st.text_area("Offre", height=200, placeholder="Exigences techniques, missions, stack...", label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    launch_btn = st.button("Lancer le Scanning ⚡", use_container_width=True)

# --- ZONE CENTRALE ---
if not launch_btn and not uploaded_files:
    st.markdown("""
<div style="padding: 1rem 2rem;">
<h1 style="color: #0F172A; font-weight: 800; font-size: 2.2rem; margin-bottom: 0.5rem;">Vue d'ensemble de l'espace de travail</h1>
<p style="color: #64748B; font-size: 1.1rem; margin-bottom: 3rem;">Le moteur d'intelligence artificielle est prêt. Suivez les étapes ci-dessous pour lancer votre campagne de scoring.</p>

<div style="display: flex; gap: 24px; margin-bottom: 40px; flex-wrap: wrap;">
<div style="flex: 1; min-width: 250px; background: white; padding: 24px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
<div style="width: 48px; height: 48px; border-radius: 10px; background: #EFF6FF; color: #3B82F6; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 800; margin-bottom: 16px;">1</div>
<h4 style="margin:0 0 8px 0; color: #0F172A; font-size: 1.1rem;">Import des Candidats</h4>
<p style="margin:0; color: #64748B; font-size: 0.9rem; line-height: 1.5;">Glissez-déposez vos fichiers PDF dans le panneau latéral gauche.</p>
</div>

<div style="flex: 1; min-width: 250px; background: white; padding: 24px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
<div style="width: 48px; height: 48px; border-radius: 10px; background: #F3E8FF; color: #A855F7; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 800; margin-bottom: 16px;">2</div>
<h4 style="margin:0 0 8px 0; color: #0F172A; font-size: 1.1rem;">Calibration de l'offre</h4>
<p style="margin:0; color: #64748B; font-size: 0.9rem; line-height: 1.5;">Collez la description précise du poste. L'IA utilisera ce texte comme référentiel.</p>
</div>

<div style="flex: 1; min-width: 250px; background: white; padding: 24px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
<div style="width: 48px; height: 48px; border-radius: 10px; background: #ECFDF5; color: #10B981; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 800; margin-bottom: 16px;">3</div>
<h4 style="margin:0 0 8px 0; color: #0F172A; font-size: 1.1rem;">Analyse & Radar</h4>
<p style="margin:0; color: #64748B; font-size: 0.9rem; line-height: 1.5;">Le moteur va générer un classement complet avec graphiques d'adéquation.</p>
</div>
</div>

<div style="background: white; border-radius: 12px; border: 2px dashed #CBD5E1; padding: 80px 20px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;">
<div style="background: #F1F5F9; width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 16px;">📈</div>
<h3 style="margin:0 0 8px 0; color: #475569; font-size: 1.2rem;">Le tableau de bord est vide</h3>
<p style="margin:0; color: #94A3B8; font-size: 0.95rem;">Cliquez sur "Lancer le Scanning" pour générer les rapports.</p>
</div>
</div>
    """, unsafe_allow_html=True)

elif launch_btn:
    if not uploaded_files or not job_description:
        st.warning("⚠️ Inputs manquants. Remplissez la barre latérale.")
    else:
        results = []
        total_files = len(uploaded_files)
        start_time = time.time()
        
        # --- CRÉATION DE LA BARRE DE PROGRESSION ---
        st.markdown("<br>", unsafe_allow_html=True)
        progress_text = "Initialisation du moteur d'analyse..."
        progress_bar = st.progress(0, text=progress_text)

        for i, file in enumerate(uploaded_files):
            # Mise à jour de la barre et du texte avant chaque CV
            current_percent = int((i / total_files) * 100)
            progress_bar.progress(current_percent, text=f"🔍 Analyse en cours : {file.name} ({i+1}/{total_files})")
            
            text = extract_text_from_pdf(file)
            if not text or len(text) < 20 or "ERREUR" in text:
                results.append({"nom": file.name, "score_final": 0, "reasoning": "Document illisible ou vide."})
            else:
                data = _process_cv_one_shot(text, job_description)
                n_coeur = min(int(data.get("n_hard_skills_coeur", 0)), 65)
                n_outils = min(int(data.get("n_outils_metier", 0)), 10)
                n_imp = min(int(data.get("n_business_impact", 0)), 10)
                n_sen = min(int(data.get("n_seniorite", 0)), 5)
                n_soft = min(int(data.get("n_soft_skills", 0)), 5)
                n_story = min(int(data.get("n_storytelling", 0)), 5)
                
                final_score = n_coeur + n_outils + n_imp + n_sen + n_soft + n_story
                data.update({"score_final": final_score, "n_coeur": n_coeur, "n_outils": n_outils, "n_imp": n_imp, "n_sen": n_sen, "n_soft": n_soft, "n_story": n_story})
                results.append(data)
        
        # --- FIN DE L'ANALYSE ---
        progress_bar.progress(100, text="✨ Analyse terminée ! Génération du tableau de bord...")
        time.sleep(0.5) # Petite pause pour laisser le temps de lire "100%"
        progress_bar.empty() # On fait disparaître la barre une fois fini pour un affichage propre
        
        end_time = time.time()

        results.sort(key=lambda x: int(x.get('score_final', 0)), reverse=True)
        
        # --- HEADER KPI DASHBOARD ---
        st.markdown(f"<h3 style='color: #0F172A; margin-bottom: 1rem; padding-left: 1rem;'>Rapport d'Analyse (Généré en {round(end_time - start_time, 1)}s)</h3>", unsafe_allow_html=True)
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(f"<div class='dash-card'><div style='color:#64748B; font-size:0.8rem; font-weight:700;'>VOLUMÉTRIE</div><div style='font-size:2rem; font-weight:800; color:#0F172A;'>{len(uploaded_files)}</div></div>", unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"<div class='dash-card'><div style='color:#64748B; font-size:0.8rem; font-weight:700;'>MEILLEUR MATCH</div><div style='font-size:2rem; font-weight:800; color:#10B981;'>{results[0].get('score_final', 0)}%</div></div>", unsafe_allow_html=True)
        with kpi3:
            avg_score = int(sum([r.get('score_final', 0) for r in results]) / len(results)) if results else 0
            st.markdown(f"<div class='dash-card'><div style='color:#64748B; font-size:0.8rem; font-weight:700;'>MOYENNE DU POOL</div><div style='font-size:2rem; font-weight:800; color:#3B82F6;'>{avg_score}%</div></div>", unsafe_allow_html=True)
        with kpi4:
            ecart = results[0].get('score_final', 0) - (results[1].get('score_final', 0) if len(results)>1 else 0)
            st.markdown(f"<div class='dash-card'><div style='color:#64748B; font-size:0.8rem; font-weight:700;'>ÉCART N°1 vs N°2</div><div style='font-size:2rem; font-weight:800; color:#F59E0B;'>+{ecart} pts</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- SPOTLIGHT : LE MEILLEUR CANDIDAT ---
        if len(results) > 0 and results[0].get('score_final', 0) > 0:
            top_cand = results[0]
            st.markdown("<h4 style='color: #0F172A; margin-bottom: 1rem; padding-left: 1rem;'>🏆 Recommandation Numéro 1</h4>", unsafe_allow_html=True)
            
            with st.container():
                st.markdown("<div class='spotlight-card' style='margin: 0 1rem;'>", unsafe_allow_html=True)
                
                spot_col1, spot_col2, spot_col3 = st.columns([1.5, 2, 1.5])
                
                with spot_col1:
                    st.markdown(f"<div style='font-size:3.5rem; font-weight:900; color:#3B82F6; line-height:1;'>{top_cand.get('score_final', 0)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='margin-top:10px; margin-bottom:0;'>{top_cand.get('nom', 'Anonyme')}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#64748B; font-weight:500;'>{top_cand.get('titre_profil', '')} • {top_cand.get('années_exp', 0)} ans</p>", unsafe_allow_html=True)
                    
                    comps = top_cand.get('compétences', [])
                    if isinstance(comps, list):
                        badges = "".join([f"<span class='badge-tech'>{c}</span>" for c in comps[:5]])
                        st.markdown(f"<div style='margin-top:15px;'>{badges}</div>", unsafe_allow_html=True)
                
                with spot_col2:
                    st.markdown("<div style='padding-top: 10px;'>", unsafe_allow_html=True)
                    bars_html = make_progress_bar("Tech Cœur", top_cand.get('n_coeur',0), 65, "#3B82F6")
                    bars_html += make_progress_bar("Outils", top_cand.get('n_outils',0), 10, "#8B5CF6")
                    bars_html += make_progress_bar("Impact ROI", top_cand.get('n_imp',0), 10, "#10B981")
                    st.markdown(bars_html, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with spot_col3:
                    st.plotly_chart(create_radar_chart(top_cand), use_container_width=True, config={'displayModeBar': False}, key="radar_top")
                
                st.markdown("<hr style='border-color: #E2E8F0; margin: 15px 0;'>", unsafe_allow_html=True)
                st.markdown(f"**Synthèse IA :** {top_cand.get('reasoning', '')}")
                st.markdown(f"<div style='color:#10B981; font-size:0.9rem; margin-top:5px;'><b>Force :</b> {top_cand.get('strength', '')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#EF4444; font-size:0.9rem;'><b>Risque :</b> {top_cand.get('risk', '')}</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True) 

        # --- RUNNER UPS ---
        if len(results) > 1:
            st.markdown("<br><h4 style='color: #0F172A; margin-bottom: 1rem; padding-left: 1rem;'>📋 Autres Profils Analysés</h4>", unsafe_allow_html=True)
            
            for idx, res in enumerate(results[1:]):
                score = res.get('score_final', 0)
                color = "#10B981" if score >= 60 else ("#F59E0B" if score >= 40 else "#EF4444")
                
                st.markdown(f"""
                <div class='dash-card' style='margin: 0 1rem 0px 1rem; display: flex; align-items: center; padding: 15px 20px; border-bottom: none; border-bottom-left-radius: 0; border-bottom-right-radius: 0;'>
                    <div style='background: {color}; color: white; border-radius: 8px; font-weight: 800; font-size: 1.2rem; padding: 8px 12px; margin-right: 20px; min-width: 60px; text-align: center;'>
                        {score}
                    </div>
                    <div style='flex-grow: 1;'>
                        <div style='font-size: 1.1rem; font-weight: 700; color: #0F172A;'>{res.get('nom', 'Anonyme')} <span style='font-weight: 400; color: #64748B; font-size: 0.9rem;'>— {res.get('titre_profil', '')}</span></div>
                        <div style='font-size: 0.85rem; color: #475569; margin-top: 4px;'><b>Tech:</b> {res.get('n_coeur',0)}/65 &nbsp;|&nbsp; <b>Outils:</b> {res.get('n_outils',0)}/10 &nbsp;|&nbsp; <b>Impact:</b> {res.get('n_imp',0)}/10</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.container():
                    st.markdown("<div style='padding: 0 1rem;'>", unsafe_allow_html=True)
                    with st.expander("📊 Voir l'analyse détaillée et le graphique"):
                        col_r1, col_r2 = st.columns([1, 1.5])
                        
                        with col_r1:
                            st.plotly_chart(create_radar_chart(res), use_container_width=True, config={'displayModeBar': False}, key=f"radar_runner_{idx}")
                        
                        with col_r2:
                            st.markdown(f"**Synthèse :** {res.get('reasoning', '')}")
                            st.markdown(f"**💪 Force :** <span style='color:#10B981;'>{res.get('strength', '-')}</span>", unsafe_allow_html=True)
                            st.markdown(f"**⚠️ Risque :** <span style='color:#EF4444;'>{res.get('risk', '-')}</span>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)