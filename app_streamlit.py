"""
Recruitment Analyst - ÉDITION DASHBOARD ENTERPRISE
Architecture Modulaire, UI/UX SaaS B2B, Persistance SQLite, Export Excel, et Mode Copilote.
"""
import streamlit as st
import json
import logging
import os
import sys
import time
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Talent AI | Enterprise Sourcing", page_icon="🧿", layout="wide", initial_sidebar_state="expanded")

# --- IMPORTS PROPRES (Modules externes) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.modules.pdf_utils import extract_text_from_pdf
    from src.modules.db_manager import init_db, create_job_offer, get_all_job_offers, save_candidate, get_candidates_by_offer, delete_candidate, delete_job_offer, update_candidate_data
    from src.modules.scoring_engine import process_cv_scoring
    from src.modules.interview_generator import generate_interview_questions
    from src.modules.ui_components import create_radar_chart, make_progress_bar
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
    [data-testid="stSidebar"] input::placeholder, 
    [data-testid="stSidebar"] textarea::placeholder { 
        color: #94A3B8 !important; 
        opacity: 0.8 !important; 
    }
    [data-testid="stFileUploadDropzone"] { background-color: #0F172A !important; border: 2px dashed #475569 !important; border-radius: 8px !important; }
    [data-testid="stFileUploadDropzone"] *, [data-testid="stFileUploadDropzone"] svg { color: #F8FAFC !important; fill: #F8FAFC !important; }
    
    /* --- BOUTONS PRINCIPAUX (Sleek, Sombre, Enterprise) --- */
    button[kind="primary"], [data-testid="stDownloadButton"] button, [data-testid="stFileUploader"] button { 
        background-color: #1E293B !important; /* Gris Ardoise foncé */
        color: #FFFFFF !important; 
        font-weight: 600 !important; 
        font-size: 0.85rem !important;
        border-radius: 6px !important; 
        border: 1px solid #0F172A !important; 
        padding: 0.4rem 0.8rem !important; 
        text-transform: uppercase; 
        transition: background-color 0.2s, transform 0.1s;
        min-height: 45px !important; /* Beaucoup plus fin */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        line-height: 1.2 !important;
        width: 100% !important;
    }
    button[kind="primary"]:hover, [data-testid="stDownloadButton"] button:hover { 
        background-color: #0F172A !important; /* Encore plus sombre au survol */
        transform: translateY(-1px); 
    }
    button[kind="primary"]:active { border-color: #EF4444 !important; } 
    
    /* --- BOUTONS SECONDAIRES DISCRETS --- */
    button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        color: #64748B !important;
        box-shadow: none !important;
        padding: 0 !important;
        min-height: 0 !important;
        text-transform: uppercase !important;
        font-size: 0.8rem !important;
        width: auto !important;
        font-weight: 700 !important;
        transition: color 0.2s;
    }
    button[kind="secondary"]:hover {
        color: #3B82F6 !important;
    }

    .dash-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); border: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)

# ==================== HELPER : PRÉPARATION EXPORT EXCEL ====================
def prepare_export_df(df_history):
    if df_history.empty:
        return pd.DataFrame()
    
    export_list = []
    for _, row in df_history.iterrows():
        try:
            data = json.loads(row['analyse_json'])
        except:
            data = {}
            
        q_data = data.get("interview_questions", {})
            
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

# ==================== INTERFACE SAAS ====================

tab1, tab2 = st.tabs(["Scanning de CV", "Gestion des Campagnes (Vivier)"])

# --- VARIABLES GLOBALES DE LA SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 900; font-size: 1.8rem; margin-bottom: 0;'>TALENT<span style='color: #3B82F6;'>.AI</span></h2>", unsafe_allow_html=True)
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
    launch_btn = st.button("Lancer le Scanning", type="primary", use_container_width=True)

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
            st.warning("Veuillez uploader au moins un CV.")
        elif offer_mode == "Créer une nouvelle offre" and (not offer_title or not job_description):
            st.warning("Veuillez remplir le titre et la description de la nouvelle offre.")
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
                progress_bar.progress(current_percent, text=f"Analyse en cours : {file.name} ({i+1}/{total_files})")
                
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
                
                time.sleep(3)
            
            progress_bar.progress(100, text="Analyse terminée ! Base de données mise à jour.")
            time.sleep(1)
            progress_bar.empty()
            st.success("Analyse terminée. Allez dans l'onglet 'Vivier' pour consulter le classement complet pour cette campagne.")

# --- ONGLET 2 : VIVIER PAR CAMPAGNE ---
with tab2:
    st.markdown("<h2 style='color: #0F172A; font-weight: 800; font-size: 2rem; margin-bottom: 1rem;'>Vivier par Campagne</h2>", unsafe_allow_html=True)
    
    all_offers = get_all_job_offers()
    
    if all_offers.empty:
        st.info("Aucune campagne n'a été créée pour le moment.")
    else:
        offer_map_vivier = dict(zip(all_offers['title'] + " (" + all_offers['created_at'].str.split().str[0] + ")", all_offers['id']))
        selected_offer_vivier = st.selectbox("Afficher les candidats de l'offre :", list(offer_map_vivier.keys()), key="vivier_select")
        filter_offer_id = offer_map_vivier[selected_offer_vivier]
        
        df_history = get_candidates_by_offer(filter_offer_id)
        job_description_vivier = all_offers[all_offers['id'] == filter_offer_id]['description'].iloc[0]
        
        # --- HEADER DU VIVIER (Boutons sans émojis) ---
        col_title, col_bulk_gen, col_bulk_del, col_export, col_del_offer = st.columns([1, 1.3, 1.3, 1.3, 1.3])
        
        with col_title:
            st.markdown(f"**Candidats scannés : {len(df_history)}**")
            
        with col_bulk_gen:
            if not df_history.empty:
                if st.button("Générer Entretiens", type="primary", use_container_width=True):
                    selected_rows = [row for _, row in df_history.iterrows() if st.session_state.get(f"select_cand_{row['id']}", False)]
                    
                    if not selected_rows:
                        st.warning("Cochez au moins un candidat dans la liste ci-dessous !")
                    else:
                        progress_bulk = st.progress(0, text="Initialisation...")
                        total_cands = len(selected_rows)
                        for i, row in enumerate(selected_rows):
                            progress_bulk.progress(int((i / total_cands) * 100), text=f"Création de l'entretien pour {row['nom']}...")
                            try:
                                cand_data = json.loads(row['analyse_json'])
                            except:
                                continue
                                
                            if "interview_questions" not in cand_data and row['score_final'] > 0:
                                questions = generate_interview_questions(cand_data, job_description_vivier)
                                if questions:
                                    cand_data["interview_questions"] = questions
                                    update_candidate_data(row['id'], cand_data) 
                                    time.sleep(2) 
                        progress_bulk.progress(100, text="Entretiens générés pour la sélection !")
                        time.sleep(1)
                        st.rerun()

        with col_bulk_del:
            if not df_history.empty:
                bulk_del_key = f"bulk_del_{filter_offer_id}"
                if bulk_del_key not in st.session_state:
                    st.session_state[bulk_del_key] = False
                
                if not st.session_state[bulk_del_key]:
                    if st.button("Supprimer Sélection", type="primary", use_container_width=True):
                        selected_rows = [row['id'] for _, row in df_history.iterrows() if st.session_state.get(f"select_cand_{row['id']}", False)]
                        if not selected_rows:
                            st.warning("Cochez au moins un candidat !")
                        else:
                            st.session_state[bulk_del_key] = True
                            st.rerun()
                else:
                    st.error("Êtes-vous sûr ?")
                    cY, cN = st.columns(2)
                    with cY:
                        if st.button("Oui", type="primary", key="yes_bulk_del", use_container_width=True):
                            selected_rows = [row['id'] for _, row in df_history.iterrows() if st.session_state.get(f"select_cand_{row['id']}", False)]
                            for cid in selected_rows:
                                delete_candidate(cid)
                            st.session_state[bulk_del_key] = False
                            st.rerun()
                    with cN:
                        if st.button("Non", type="secondary", key="no_bulk_del", use_container_width=True):
                            st.session_state[bulk_del_key] = False
                            st.rerun()

        with col_export:
            if not df_history.empty:
                df_export = prepare_export_df(df_history)
                csv_data = df_export.to_csv(index=False, sep=';', encoding='utf-8-sig')
                st.download_button(
                    label="Exporter vers Excel",
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
                if st.button("Supprimer Campagne", type="primary", key=f"btn_{offer_del_key}", use_container_width=True):
                    st.session_state[offer_del_key] = True
                    st.rerun()
            else:
                st.error("Supprimer ?")
                cY, cN = st.columns(2)
                with cY:
                    if st.button("Oui", type="primary", key=f"yes_{offer_del_key}", use_container_width=True):
                        delete_job_offer(filter_offer_id)
                        st.session_state[offer_del_key] = False
                        st.rerun()
                with cN:
                    if st.button("Non", type="secondary", key=f"no_{offer_del_key}", use_container_width=True):
                        st.session_state[offer_del_key] = False
                        st.rerun()

        st.markdown("<hr style='border-color: #E2E8F0; margin: 10px 0;'>", unsafe_allow_html=True)

        # --- ZONE LISTE DES CANDIDATS ---
        if df_history.empty:
            st.info("Aucun candidat n'a encore été analysé pour cette campagne.")
        else:
            all_selected = True
            for _, row in df_history.iterrows():
                if not st.session_state.get(f"select_cand_{row['id']}", False):
                    all_selected = False
                    break
            
            master_val = st.checkbox("Tout sélectionner", value=all_selected)
            
            if master_val != all_selected:
                for _, row in df_history.iterrows():
                    st.session_state[f"select_cand_{row['id']}"] = master_val
                st.rerun()
            
            for index, row in df_history.iterrows():
                score = row['score_final']
                color = "#10B981" if score >= 60 else ("#F59E0B" if score >= 40 else "#EF4444")
                
                try:
                    cand_data = json.loads(row['analyse_json'])
                except:
                    cand_data = {}
                
                col_chk, col_card = st.columns([0.5, 11.5])
                
                with col_chk:
                    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
                    st.checkbox(" ", key=f"select_cand_{row['id']}", label_visibility="collapsed")
                
                with col_card:
                    st.markdown(f"""
                    <div class='dash-card' style='margin: 0px 0 10px 0; display: flex; align-items: center; padding: 15px 20px;'>
                        <div style='background: {color}; color: white; border-radius: 8px; font-weight: 800; font-size: 1.2rem; padding: 8px 12px; margin-right: 20px; min-width: 60px; text-align: center;'>{score}</div>
                        <div style='flex-grow: 1;'>
                            <div style='font-size: 1.1rem; font-weight: 700; color: #0F172A;'>{row['nom']} <span style='font-weight: 400; color: #64748B; font-size: 0.9rem;'>— {row['titre_profil']}</span></div>
                            <div style='font-size: 0.85rem; color: #475569; margin-top: 4px;'><b>Scanné le :</b> {row['date_scan']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(f"Voir l'analyse détaillée de {row['nom']}"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**Preuve d'Ingénierie :** {cand_data.get('preuve_ingenierie', 'Non précisé')}")
                            st.markdown(f"**Force :** <span style='color:#10B981;'>{cand_data.get('strength', '-')}</span>", unsafe_allow_html=True)
                            st.markdown(f"**Risque :** <span style='color:#EF4444;'>{cand_data.get('risk', '-')}</span>", unsafe_allow_html=True)
                            st.markdown(f"**Conclusion :** {cand_data.get('reasoning', '')}")
                        with col2:
                            st.plotly_chart(create_radar_chart(cand_data), use_container_width=True, config={'displayModeBar': False}, key=f"hist_radar_{row['id']}")
                        
                        st.markdown("<hr style='border-color: #E2E8F0; margin: 15px 0;'>", unsafe_allow_html=True)
                        
                        q_data = cand_data.get("interview_questions")
                        
                        if not q_data and score > 0:
                            st.markdown("<div style='padding:10px; color:#64748B; font-style:italic;'>Questions non générées. Cochez ce candidat et utilisez le bouton 'Générer Entretiens' en haut de la page.</div>", unsafe_allow_html=True)
                        elif q_data:
                            st.markdown("<div style='background-color:#F8FAFC; padding:15px; border-radius:8px; border:1px solid #E2E8F0;'>", unsafe_allow_html=True)
                            st.markdown("#### Questions d'entretien suggérées par l'IA")
                            for key in ["q1_force", "q2_risque", "q3_situation"]:
                                if key in q_data:
                                    st.markdown(f"**{q_data[key].get('titre', '')}**")
                                    st.markdown(f"*« {q_data[key].get('question', '')} »*")
                                    st.markdown(f"**À valider :** {q_data[key].get('attente', '')}")
                                    st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        cand_del_key = f"del_cand_{row['id']}"
                        if cand_del_key not in st.session_state:
                            st.session_state[cand_del_key] = False
                            
                        if not st.session_state[cand_del_key]:
                            if st.button(f"Supprimer ce candidat", type="secondary", key=f"btn_{cand_del_key}"):
                                st.session_state[cand_del_key] = True
                                st.rerun()
                        else:
                            st.warning("Confirmer la suppression ?")
                            cY, cN = st.columns([1, 1])
                            with cY:
                                if st.button("Oui, supprimer", type="primary", key=f"yes_{cand_del_key}"):
                                    delete_candidate(row['id'])
                                    st.session_state[cand_del_key] = False
                                    st.rerun()
                            with cN:
                                if st.button("Annuler", type="secondary", key=f"no_{cand_del_key}"):
                                    st.session_state[cand_del_key] = False
                                    st.rerun()