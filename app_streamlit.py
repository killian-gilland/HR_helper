"""
Recruitment Analyst - ÉDITION DASHBOARD ENTERPRISE
Architecture Modulaire, UI/UX SaaS B2B, Persistance SQLite, et Export CSV/Excel.
"""
import streamlit as st
import json
import logging
import os
import sys
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Talent AI | Enterprise Sourcing", page_icon="🧿", layout="wide", initial_sidebar_state="expanded")

# --- IMPORTS PROPRES (Modules externes) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.modules.pdf_utils import extract_text_from_pdf
    from src.modules.db_manager import init_db, create_job_offer, get_all_job_offers, save_candidate, get_candidates_by_offer, delete_candidate, delete_job_offer
    from src.modules.scoring_engine import process_cv_scoring
    from src.modules.ui_components import create_radar_chart, make_progress_bar
    import pandas as pd
except ImportError as e:
    st.error(f"Erreur d'import : {e}. Assurez-vous que les fichiers existent dans src/modules/")
    st.stop()

logging.basicConfig(level=logging.INFO)

# Initialisation BDD
init_db()

# --- INJECTION CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif !important;}
    .stApp {background-color: #F8FAFC !important;}
    #MainMenu, header, footer {display: none !important;}
    .block-container {padding-top: 1.5rem !important; max-width: 1400px !important;}
    
    [data-testid="stSidebar"] { background-color: #0B1120 !important; border-right: 1px solid #1E293B !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color: #F8FAFC !important; }
    
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea, [data-testid="stSidebar"] select { background-color: #1E293B !important; color: #FFFFFF !important; border: 1px solid #475569 !important; border-radius: 8px !important; }
    [data-testid="stFileUploadDropzone"] { background-color: #0F172A !important; border: 2px dashed #475569 !important; border-radius: 8px !important; }
    [data-testid="stFileUploadDropzone"] *, [data-testid="stFileUploadDropzone"] svg { color: #F8FAFC !important; fill: #F8FAFC !important; }
    [data-testid="stFileUploader"] button { background-color: #3B82F6 !important; color: #FFFFFF !important; border-radius: 6px !important; }
    
    .stButton > button { background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important; color: white !important; font-weight: 700 !important; border-radius: 6px !important; border: 1px solid #1E40AF !important; padding: 0.8rem 0 !important; text-transform: uppercase; transition: transform 0.2s;}
    .stButton > button:hover { transform: translateY(-2px); }
    
    .dash-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); border: 1px solid #E2E8F0; }
    .spotlight-card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border: 2px solid #3B82F6; position: relative; }
    .meter-container { background: #E2E8F0; border-radius: 4px; height: 8px; width: 100%; margin-top: 4px; margin-bottom: 12px; overflow: hidden; }
    .meter-fill { height: 100%; border-radius: 4px; }
    [data-testid="stExpander"] { border: 1px solid #E2E8F0 !important; border-radius: 8px !important; background: #F8FAFC !important; margin-bottom: 15px !important; }
</style>
""", unsafe_allow_html=True)

# ==================== HELPER : PRÉPARATION EXPORT EXCEL ====================
def prepare_export_df(df_history):
    """Aplatit le JSON de la base de données pour créer un tableau Excel propre."""
    if df_history.empty:
        return pd.DataFrame()
    
    export_list = []
    for _, row in df_history.iterrows():
        try:
            data = json.loads(row['analyse_json'])
        except:
            data = {}
            
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
            "Conclusion IA": data.get("reasoning", "")
        })
    return pd.DataFrame(export_list)

# ==================== INTERFACE SAAS ====================

tab1, tab2 = st.tabs(["⚡ Scanning de CV", "🗄️ Gestion des Campagnes (Vivier)"])

# --- VARIABLES GLOBALES DE LA SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 900; font-size: 1.8rem; margin-bottom: 0;'>🧿 TALENT<span style='color: #3B82F6;'>.AI</span></h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 0.75rem; font-weight: 600; margin-top: 0; margin-bottom: 30px; letter-spacing: 1px;'>ENTERPRISE SOURCING ENGINE</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>1. Choix de la Campagne</p>", unsafe_allow_html=True)
    offers_df = get_all_job_offers()
    
    offer_mode = st.radio("Mode :", ["Créer une nouvelle offre", "Reprendre une offre existante"], label_visibility="collapsed")
    
    current_offer_id = None
    job_description = ""
    offer_title = ""
    
    if offer_mode == "Créer une nouvelle offre":
        offer_title = st.text_input("Titre du poste (ex: Lead Data Scientist)", placeholder="Titre de l'offre")
        job_description = st.text_area("Description du poste", height=150, placeholder="Collez l'offre d'emploi ici...")
    else:
        if offers_df.empty:
            st.warning("Aucune campagne existante.")
        else:
            offer_map = dict(zip(offers_df['title'] + " (" + offers_df['created_at'].str.split().str[0] + ")", offers_df['id']))
            selected_offer = st.selectbox("Sélectionnez l'offre :", list(offer_map.keys()))
            current_offer_id = offer_map[selected_offer]
            job_description = offers_df[offers_df['id'] == current_offer_id]['description'].iloc[0]
            st.text_area("Description (Lecture seule)", job_description, height=150, disabled=True)

    st.markdown("<br><p style='font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>2. Base de CV (PDF)</p>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    launch_btn = st.button("Lancer le Scanning ⚡", use_container_width=True)

# --- ONGLET 1 : SCAN ---
with tab1:
    if not launch_btn and not uploaded_files:
        st.markdown("""
        <div style="padding: 1rem 2rem;">
        <h1 style="color: #0F172A; font-weight: 800; font-size: 2.2rem; margin-bottom: 0.5rem;">Espace de travail IA</h1>
        <p style="color: #64748B; font-size: 1.1rem; margin-bottom: 2rem;">Créez une campagne ou sélectionnez-en une existante à gauche pour analyser de nouveaux CV.</p>
        </div>
        """, unsafe_allow_html=True)

    elif launch_btn:
        if not uploaded_files:
            st.warning("⚠️ Veuillez uploader au moins un CV.")
        elif offer_mode == "Créer une nouvelle offre" and (not offer_title or not job_description):
            st.warning("⚠️ Veuillez remplir le titre et la description de la nouvelle offre.")
        else:
            if offer_mode == "Créer une nouvelle offre":
                current_offer_id = create_job_offer(offer_title, job_description)
                st.success(f"Campagne '{offer_title}' créée avec succès !")
            
            results = []
            total_files = len(uploaded_files)
            
            st.markdown("<br>", unsafe_allow_html=True)
            progress_bar = st.progress(0, text="Initialisation du moteur d'analyse...")

            for i, file in enumerate(uploaded_files):
                current_percent = int((i / total_files) * 100)
                progress_bar.progress(current_percent, text=f"🔍 Analyse en cours : {file.name} ({i+1}/{total_files})")
                
                text = extract_text_from_pdf(file)
                if not text or len(text) < 20 or "ERREUR" in text:
                    results.append({"nom": file.name, "score_final": 0, "reasoning": "Document illisible ou vide."})
                else:
                    data = process_cv_scoring(text, job_description)
                    n_coeur = min(int(data.get("n_hard_skills_coeur", 0)), 65)
                    n_outils = min(int(data.get("n_outils_metier", 0)), 10)
                    n_imp = min(int(data.get("n_business_impact", 0)), 10)
                    n_sen = min(int(data.get("n_seniorite", 0)), 5)
                    n_soft = min(int(data.get("n_soft_skills", 0)), 5)
                    n_story = min(int(data.get("n_storytelling", 0)), 5)
                    
                    final_score = n_coeur + n_outils + n_imp + n_sen + n_soft + n_story
                    data.update({"score_final": final_score, "n_coeur": n_coeur, "n_outils": n_outils, "n_imp": n_imp, "n_sen": n_sen, "n_soft": n_soft, "n_story": n_story})
                    
                    save_candidate(data, current_offer_id)
                    results.append(data)
                
                # Respiration du GPU pour éviter les Timeout
                if i < total_files - 1:
                    time.sleep(3)
            
            progress_bar.progress(100, text="✨ Analyse terminée ! Base de données mise à jour.")
            time.sleep(1)
            progress_bar.empty()
            
            st.success("Analyse terminée. Allez dans l'onglet 'Vivier' pour consulter le classement complet pour cette campagne.")

# --- ONGLET 2 : VIVIER PAR CAMPAGNE ---
with tab2:
    st.markdown("<h2 style='color: #0F172A; font-weight: 800; font-size: 2rem; margin-bottom: 1rem;'>🗄️ Vivier par Campagne</h2>", unsafe_allow_html=True)
    
    all_offers = get_all_job_offers()
    
    if all_offers.empty:
        st.info("Aucune campagne n'a été créée pour le moment.")
    else:
        offer_map_vivier = dict(zip(all_offers['title'] + " (" + all_offers['created_at'].str.split().str[0] + ")", all_offers['id']))
        selected_offer_vivier = st.selectbox("📍 Afficher les candidats de l'offre :", list(offer_map_vivier.keys()), key="vivier_select")
        filter_offer_id = offer_map_vivier[selected_offer_vivier]
        
        df_history = get_candidates_by_offer(filter_offer_id)
        
        # --- HEADER DU VIVIER (Boutons d'action) ---
        col_title, col_export, col_del_offer = st.columns([2, 1, 1])
        
        with col_title:
            st.markdown(f"**Total des candidats pour ce poste : {len(df_history)}**")
            
        with col_export:
            # ⚡ NOUVEAU : BOUTON D'EXPORT CSV
            if not df_history.empty:
                df_export = prepare_export_df(df_history)
                # Encodage utf-8-sig et séparateur point-virgule pour Excel Français
                csv_data = df_export.to_csv(index=False, sep=';', encoding='utf-8-sig')
                st.download_button(
                    label="📥 Exporter vers Excel (CSV)",
                    data=csv_data,
                    file_name=f"candidats_campagne_{filter_offer_id}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
        with col_del_offer:
            offer_del_key = f"del_offer_{filter_offer_id}"
            if offer_del_key not in st.session_state:
                st.session_state[offer_del_key] = False
                
            if not st.session_state[offer_del_key]:
                if st.button("🗑️ Supprimer la campagne", key=f"btn_{offer_del_key}", use_container_width=True):
                    st.session_state[offer_del_key] = True
                    st.rerun()
            else:
                st.error("⚠️ Supprimer la campagne ?")
                cY, cN = st.columns(2)
                with cY:
                    if st.button("✅ Oui", key=f"yes_{offer_del_key}", use_container_width=True):
                        delete_job_offer(filter_offer_id)
                        st.session_state[offer_del_key] = False
                        st.rerun()
                with cN:
                    if st.button("❌ Non", key=f"no_{offer_del_key}", use_container_width=True):
                        st.session_state[offer_del_key] = False
                        st.rerun()

        st.markdown("<hr style='border-color: #E2E8F0; margin: 10px 0;'>", unsafe_allow_html=True)

        # --- LISTE DES CANDIDATS ---
        if df_history.empty:
            st.info("Aucun candidat n'a encore été analysé pour cette campagne.")
        else:
            for index, row in df_history.iterrows():
                score = row['score_final']
                color = "#10B981" if score >= 60 else ("#F59E0B" if score >= 40 else "#EF4444")
                
                try:
                    cand_data = json.loads(row['analyse_json'])
                except:
                    cand_data = {}
                
                st.markdown(f"""
                <div class='dash-card' style='margin: 10px 0; display: flex; align-items: center; padding: 15px 20px;'>
                    <div style='background: {color}; color: white; border-radius: 8px; font-weight: 800; font-size: 1.2rem; padding: 8px 12px; margin-right: 20px; min-width: 60px; text-align: center;'>{score}</div>
                    <div style='flex-grow: 1;'>
                        <div style='font-size: 1.1rem; font-weight: 700; color: #0F172A;'>{row['nom']} <span style='font-weight: 400; color: #64748B; font-size: 0.9rem;'>— {row['titre_profil']}</span></div>
                        <div style='font-size: 0.85rem; color: #475569; margin-top: 4px;'><b>Scanné le :</b> {row['date_scan']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"📊 Voir l'analyse de {row['nom']}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**🧠 Preuve d'Ingénierie :** {cand_data.get('preuve_ingenierie', 'Non précisé')}")
                        st.markdown(f"**💪 Force :** <span style='color:#10B981;'>{cand_data.get('strength', '-')}</span>", unsafe_allow_html=True)
                        st.markdown(f"**⚠️ Risque :** <span style='color:#EF4444;'>{cand_data.get('risk', '-')}</span>", unsafe_allow_html=True)
                        st.markdown(f"**📝 Conclusion :** {cand_data.get('reasoning', '')}")
                    with col2:
                        st.plotly_chart(create_radar_chart(cand_data), use_container_width=True, config={'displayModeBar': False}, key=f"hist_radar_{row['id']}")
                    
                    cand_del_key = f"del_cand_{row['id']}"
                    if cand_del_key not in st.session_state:
                        st.session_state[cand_del_key] = False
                        
                    if not st.session_state[cand_del_key]:
                        if st.button(f"🗑️ Supprimer ce candidat", key=f"btn_{cand_del_key}"):
                            st.session_state[cand_del_key] = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Confirmer la suppression ?")
                        cY, cN = st.columns([1, 1])
                        with cY:
                            if st.button("✅ Oui, supprimer", key=f"yes_{cand_del_key}"):
                                delete_candidate(row['id'])
                                st.session_state[cand_del_key] = False
                                st.rerun()
                        with cN:
                            if st.button("❌ Annuler", key=f"no_{cand_del_key}"):
                                st.session_state[cand_del_key] = False
                                st.rerun()