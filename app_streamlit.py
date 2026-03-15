"""
Recruitment Analyst - ÉDITION BILINGUE (FR/EN)
SaaS Multi-Tenant, UI/UX B2B, Export Excel, Shortlist, i18n (Internationalisation).
"""
import streamlit as st
import json
import logging
import os
import sys
import time
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Talent AI | Enterprise Sourcing", 
    page_icon="🧿", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- IMPORTS PROPRES ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.modules.pdf_utils import extract_text_from_pdf
    from src.modules.db_manager import (
        init_db, create_user, verify_user, create_job_offer, 
        get_all_job_offers, save_candidate, get_candidates_by_offer, 
        delete_candidate, delete_job_offer, update_candidate_data
    )
    from src.modules.scoring_engine import process_cv_scoring
    from src.modules.interview_generator import generate_interview_questions
    from src.modules.ui_components import create_radar_chart
except ImportError as e:
    st.error(f"Erreur d'import : {e}. Assurez-vous que les fichiers existent dans src/modules/")
    st.stop()

logging.basicConfig(level=logging.INFO)
init_db()

# ==================== DICTIONNAIRE DE TRADUCTION (i18n) ====================
if 'lang' not in st.session_state:
    st.session_state.lang = 'fr'

T = {
    'fr': {
        'tab_scan': "Scanning de CV", 
        'tab_pool': "Gestion des Campagnes (Vivier)",
        'login_welcome': "### Bienvenue", 
        'login_new': "### Nouvel Espace",
        'id': "Identifiant", 
        'pass': "Mot de passe", 
        'connect': "Se connecter",
        'company': "Nom de l'entreprise", 
        'id_wanted': "Identifiant souhaité", 
        'create_space': "Créer l'espace client",
        'err_creds': "Identifiants incorrects.", 
        'succ_acct': "Compte créé ! Connectez-vous dans l'onglet 'Connexion'.",
        'err_exist': "Cet identifiant existe déjà.", 
        'err_fill': "Veuillez remplir tous les champs.",
        'sb_step1': "1. Choix de la Campagne", 
        'sb_mode': "Mode :",
        'sb_new_offer': "Créer une nouvelle offre", 
        'sb_old_offer': "Reprendre une offre existante",
        'sb_title': "Titre du poste (ex: Lead Data Scientist)", 
        'sb_desc': "Description du poste",
        'sb_no_camp': "Aucune campagne existante.", 
        'sb_select': "Sélectionnez l'offre :",
        'sb_step2': "2. Base de CV (PDF)", 
        'btn_launch': "Lancer le Scanning", 
        'btn_logout': "🚪 Déconnexion",
        'hello': "Bonjour, {} 👋", 
        'hello_sub': "Vos données sont isolées dans votre espace de travail sécurisé. Créez une campagne pour commencer.",
        'warn_no_cv': "Veuillez uploader au moins un CV.", 
        'warn_no_title': "Veuillez remplir le titre et la description de la nouvelle offre.",
        'succ_camp': "Campagne '{}' créée avec succès !", 
        'prog_init': "Initialisation du moteur d'analyse...",
        'prog_scan': "Analyse en cours : {} ({}/{})", 
        'err_doc': "Document illisible ou vide.",
        'succ_done': "Analyse terminée ! Mise à jour du vivier...",
        'pool_title': "Vivier par Campagne", 
        'pool_no_camp': "Aucune campagne n'a été créée pour le moment.",
        'pool_show': "Afficher les candidats de l'offre :", 
        'pool_total': "**Candidats scannés : {}**",
        'btn_gen': "Générer Entretiens", 
        'btn_del_sel': "Supprimer Sélection", 
        'btn_export': "Exporter vers Excel", 
        'btn_del_camp': "Supprimer Campagne",
        'warn_check': "Cochez au moins un candidat !", 
        'prog_gen': "Création de l'entretien pour {}...",
        'succ_gen': "Entretiens générés pour la sélection !", 
        'ask_sure': "Êtes-vous sûr ?", 
        'yes': "Oui", 
        'no': "Non",
        'pool_no_cand': "Aucun candidat n'a encore été analysé pour cette campagne.",
        'filt_title': "Filtres et Tris", 
        'filt_top': "🏆 Afficher le Top X des candidats :",
        'filt_sort': "↕️ Trier l'affichage :", 
        'btn_apply': "Appliquer", 
        'warn_empty': "Aucun candidat trouvé.",
        'chk_all': "Tout sélectionner ({} candidats affichés)", 
        'scanned_on': "Scanné le :",
        'exp_see': "Voir l'analyse détaillée de {}", 
        'exp_proof': "**Preuve d'Ingénierie :** {}",
        'exp_strength': "**Force :**", 
        'exp_risk': "**Risque :**", 
        'exp_conc': "**Conclusion :**",
        'exp_no_q': "Questions non générées. Cochez ce candidat et utilisez le bouton 'Générer Entretiens' en haut.",
        'exp_q_title': "#### Questions d'entretien suggérées par l'IA", 
        'exp_expect': "**À valider :**",
        'btn_del_cand': "Supprimer ce candidat", 
        'sort_desc': "Score : Du meilleur au moins bon",
        'sort_asc': "Score : Du moins bon au meilleur", 
        'sort_az': "Nom : Ordre alphabétique (A-Z)"
    },
    'en': {
        'tab_scan': "CV Scanning", 
        'tab_pool': "Campaign Management (Talent Pool)",
        'login_welcome': "### Welcome Back", 
        'login_new': "### New Workspace",
        'id': "Username", 
        'pass': "Password", 
        'connect': "Log In",
        'company': "Company Name", 
        'id_wanted': "Desired Username", 
        'create_space': "Create Workspace",
        'err_creds': "Incorrect credentials.", 
        'succ_acct': "Account created! You can now log in.",
        'err_exist': "This username already exists.", 
        'err_fill': "Please fill in all fields.",
        'sb_step1': "1. Campaign Selection", 
        'sb_mode': "Mode:",
        'sb_new_offer': "Create a new job offer", 
        'sb_old_offer': "Select an existing offer",
        'sb_title': "Job Title (e.g., Lead Data Scientist)", 
        'sb_desc': "Job Description",
        'sb_no_camp': "No existing campaigns.", 
        'sb_select': "Select offer:",
        'sb_step2': "2. Resume Database (PDF)", 
        'btn_launch': "Start Scanning", 
        'btn_logout': "🚪 Log Out",
        'hello': "Hello, {} 👋", 
        'hello_sub': "Your data is isolated in your secure workspace. Create a campaign to begin.",
        'warn_no_cv': "Please upload at least one CV.", 
        'warn_no_title': "Please provide a title and description for the new offer.",
        'succ_camp': "Campaign '{}' successfully created!", 
        'prog_init': "Initializing analysis engine...",
        'prog_scan': "Analyzing: {} ({}/{})", 
        'err_doc': "Unreadable or empty document.",
        'succ_done': "Analysis complete! Updating talent pool...",
        'pool_title': "Talent Pool by Campaign", 
        'pool_no_camp': "No campaigns created yet.",
        'pool_show': "Show candidates for:", 
        'pool_total': "**Total Candidates: {}**",
        'btn_gen': "Generate Interviews", 
        'btn_del_sel': "Delete Selected", 
        'btn_export': "Export to Excel", 
        'btn_del_camp': "Delete Campaign",
        'warn_check': "Select at least one candidate!", 
        'prog_gen': "Creating interview for {}...",
        'succ_gen': "Interviews generated successfully!", 
        'ask_sure': "Are you sure?", 
        'yes': "Yes", 
        'no': "No",
        'pool_no_cand': "No candidates analyzed for this campaign yet.",
        'filt_title': "Filters and Sorting", 
        'filt_top': "🏆 Show Top X candidates:",
        'filt_sort': "↕️ Sort display:", 
        'btn_apply': "Apply", 
        'warn_empty': "No candidates found.",
        'chk_all': "Select all ({} candidates shown)", 
        'scanned_on': "Scanned on:",
        'exp_see': "View detailed analysis for {}", 
        'exp_proof': "**Engineering Proof:** {}",
        'exp_strength': "**Strength:**", 
        'exp_risk': "**Risk:**", 
        'exp_conc': "**Conclusion:**",
        'exp_no_q': "No questions generated. Select this candidate and click 'Generate Interviews' above.",
        'exp_q_title': "#### AI-Suggested Interview Questions", 
        'exp_expect': "**What to look for:**",
        'btn_del_cand': "Delete candidate", 
        'sort_desc': "Score: Highest to Lowest",
        'sort_asc': "Score: Lowest to Highest", 
        'sort_az': "Name: Alphabetical (A-Z)"
    }
}

# Fonction de traduction
def t(key):
    return T[st.session_state.lang].get(key, key)

# --- INJECTION CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif !important;}
    .stApp {background-color: #F8FAFC !important;}
    #MainMenu, footer {display: none !important;} 
    
    header {background-color: transparent !important;}
    
    /* Espacement de base de l'application (modifié dynamiquement si déconnecté) */
    .block-container {padding-top: 4.5rem !important; max-width: 1400px !important;}
    
    [data-testid="stSidebar"] { background-color: #0B1120 !important; border-right: 1px solid #1E293B !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color: #F8FAFC !important; }
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea, [data-testid="stSidebar"] select { background-color: #1E293B !important; color: #FFFFFF !important; border: 1px solid #475569 !important; border-radius: 8px !important; }
    [data-testid="stSidebar"] input::placeholder, [data-testid="stSidebar"] textarea::placeholder { color: #94A3B8 !important; opacity: 0.8 !important; }

    [data-testid="stFileUploadDropzone"] { background-color: #0F172A !important; border: 2px dashed #475569 !important; border-radius: 8px !important; }
    [data-testid="stFileUploadDropzone"] *, [data-testid="stFileUploadDropzone"] svg { color: #F8FAFC !important; fill: #F8FAFC !important; }
    
    /* BOUTONS PRINCIPAUX */
    button[kind="primary"], [data-testid="stDownloadButton"] button, [data-testid="stFileUploader"] button { 
        background-color: #1E293B !important; color: #FFFFFF !important; font-weight: 600 !important; font-size: 0.85rem !important;
        border-radius: 6px !important; border: 1px solid #0F172A !important; padding: 0.4rem 0.8rem !important; text-transform: uppercase; 
        transition: background-color 0.2s, transform 0.1s; min-height: 45px !important; display: flex !important;
        align-items: center !important; justify-content: center !important; text-align: center !important; width: 100% !important;
    }
    button[kind="primary"]:hover, [data-testid="stDownloadButton"] button:hover { background-color: #0F172A !important; transform: translateY(-1px); }
    button[kind="primary"]:active { border-color: #EF4444 !important; } 
    
    /* BOUTONS SECONDAIRES */
    button[kind="secondary"] {
        background: transparent !important; border: none !important; color: #64748B !important; box-shadow: none !important; 
        padding: 0 !important; min-height: 0 !important; text-transform: uppercase !important; font-size: 0.8rem !important; 
        width: auto !important; font-weight: 700 !important; transition: color 0.2s;
    }
    button[kind="secondary"]:hover { color: #3B82F6 !important; }

    /* ⚡ LES DRAPEAUX EN HAUT A DROITE (Encore plus gros !) */
    .lang-btn button, .lang-btn button p, .lang-btn button span { font-size: 3.5rem !important; margin: 0 !important; padding: 0 !important;}
    .lang-btn button { background: transparent !important; border: none !important; transition: transform 0.2s;}
    .lang-btn button:hover { transform: scale(1.1); }

    /* LES CARTES */
    .dash-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1); border: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)

# ==================== SÉLECTEUR DE LANGUE (EN HAUT À DROITE) ====================
col_spacer, col_fr, col_en = st.columns([10, 1, 1])
with col_fr:
    st.markdown("<div class='lang-btn'>", unsafe_allow_html=True)
    if st.button("🇫🇷", type="secondary", key="btn_fr"):
        st.session_state.lang = 'fr'
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_en:
    st.markdown("<div class='lang-btn'>", unsafe_allow_html=True)
    if st.button("🇬🇧", type="secondary", key="btn_en"):
        st.session_state.lang = 'en'
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== HELPER : PRÉPARATION EXPORT EXCEL ====================
def prepare_export_df(df_history):
    if df_history.empty:
        return pd.DataFrame()
        
    export_list = []
    for idx, row in df_history.iterrows():
        try:
            data = json.loads(row['analyse_json'])
        except:
            data = {}
            
        q_data = data.get("interview_questions", {})
        
        if st.session_state.lang == 'en':
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

# ==================== GESTION DE SESSION (LOGIN) ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.company_name = None

def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.company_name = None
    st.session_state.confirm_logout = False
    st.rerun()

# ==================== ÉCRAN DE CONNEXION ====================
if not st.session_state.logged_in:
    # ⚡ OVERRIDE CSS : On remonte le contenu spécifiquement sur la page de connexion
    st.markdown("<style>.block-container {padding-top: 1rem !important;}</style>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #0F172A;'>TALENT<span style='color: #3B82F6;'>.AI</span></h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # On utilise les colonnes pour centrer le formulaire sans créer de bug d'affichage HTML
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    
    with col2:
        tab_login_title = "Connexion" if st.session_state.lang == 'fr' else "Log In"
        tab_signup_title = "Créer un compte" if st.session_state.lang == 'fr' else "Sign Up"
        
        auth_tab1, auth_tab2 = st.tabs([tab_login_title, tab_signup_title])
        
        with auth_tab1:
            st.markdown(t('login_welcome'))
            log_user = st.text_input(t('id'), key="log_user")
            log_pass = st.text_input(t('pass'), type="password", key="log_pass")
            
            if st.button(t('connect'), type="primary"):
                user = verify_user(log_user, log_pass)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.company_name = user[1]
                    st.rerun()
                else:
                    st.error(t('err_creds'))
                    
        with auth_tab2:
            st.markdown(t('login_new'))
            reg_comp = st.text_input(t('company'), key="reg_comp")
            reg_user = st.text_input(t('id_wanted'), key="reg_user")
            reg_pass = st.text_input(t('pass'), type="password", key="reg_pass_new")
            
            if st.button(t('create_space'), type="primary"):
                if reg_comp and reg_user and reg_pass:
                    success = create_user(reg_user, reg_pass, reg_comp)
                    if success:
                        st.success(t('succ_acct'))
                    else:
                        st.error(t('err_exist'))
                else:
                    st.warning(t('err_fill'))
                    
    st.stop()

# ==================== INTERFACE SAAS PRINCIPALE ====================
tab1, tab2 = st.tabs([t('tab_scan'), t('tab_pool')])

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 900; font-size: 1.8rem; margin-bottom: 0;'>TALENT<span style='color: #3B82F6;'>.AI</span></h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #10B981; font-size: 0.8rem; font-weight: 700; margin-top: 5px; margin-bottom: 30px;'>🟢 ESPACE : {st.session_state.company_name.upper()}</p>", unsafe_allow_html=True)
    
    st.markdown(f"<p style='font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>{t('sb_step1')}</p>", unsafe_allow_html=True)
    
    offers_df = get_all_job_offers(st.session_state.user_id)
    offer_mode = st.radio(t('sb_mode'), [t('sb_new_offer'), t('sb_old_offer')], label_visibility="collapsed")
    
    current_offer_id = None
    job_description = ""
    offer_title = ""
    
    if offer_mode == t('sb_new_offer'):
        offer_title = st.text_input(t('sb_title'), placeholder="Lead Data Scientist")
        job_description = st.text_area(t('sb_desc'), height=150)
    else:
        if offers_df.empty:
            st.warning(t('sb_no_camp'))
        else:
            offer_map = dict(zip(offers_df['title'] + " (" + offers_df['created_at'].str.split().str[0] + ")", offers_df['id']))
            selected_offer = st.selectbox(t('sb_select'), list(offer_map.keys()))
            current_offer_id = offer_map[selected_offer]
            job_description = offers_df[offers_df['id'] == current_offer_id]['description'].iloc[0]
            st.text_area(t('sb_desc'), job_description, height=150, disabled=True)

    st.markdown(f"<br><p style='font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>{t('sb_step2')}</p>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    launch_btn = st.button(t('btn_launch'), type="primary", use_container_width=True)
    
    st.markdown("<br><hr style='border-color: #475569;'>", unsafe_allow_html=True)
    
    if 'confirm_logout' not in st.session_state:
        st.session_state.confirm_logout = False

    if not st.session_state.confirm_logout:
        if st.button(t('btn_logout'), type="secondary"):
            st.session_state.confirm_logout = True
            st.rerun()
    else:
        st.warning(t('ask_sure'))
        c_yes, c_no = st.columns(2)
        with c_yes:
            if st.button(t('yes'), type="primary", key="btn_yes_log"):
                logout()
        with c_no:
            if st.button(t('no'), type="secondary", key="btn_no_log"):
                st.session_state.confirm_logout = False
                st.rerun()

# --- ONGLET 1 : SCAN ---
with tab1:
    if not launch_btn and not uploaded_files:
        st.markdown(f"""
        <div style="padding: 1rem 2rem;">
        <h1 style="color: #0F172A; font-weight: 800; font-size: 2.2rem; margin-bottom: 0.5rem;">{t('hello').format(st.session_state.company_name)}</h1>
        <p style="color: #64748B; font-size: 1.1rem; margin-bottom: 2rem;">{t('hello_sub')}</p>
        </div>
        """, unsafe_allow_html=True)

    elif launch_btn:
        if not uploaded_files:
            st.warning(t('warn_no_cv'))
        elif offer_mode == t('sb_new_offer') and (not offer_title or not job_description):
            st.warning(t('warn_no_title'))
        else:
            if offer_mode == t('sb_new_offer'):
                current_offer_id = create_job_offer(offer_title, job_description, st.session_state.user_id)
                st.success(t('succ_camp').format(offer_title))
            
            results = []
            total_files = len(uploaded_files)
            
            st.markdown("<br>", unsafe_allow_html=True)
            progress_bar = st.progress(0, text=t('prog_init'))

            for i, file in enumerate(uploaded_files):
                progress_bar.progress(int((i / total_files) * 100), text=t('prog_scan').format(file.name, i+1, total_files))
                
                text = extract_text_from_pdf(file)
                if not text or len(text) < 20 or "ERREUR" in text:
                    results.append({"nom": file.name, "score_final": 0, "reasoning": t('err_doc')})
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
                
                time.sleep(20) 
            
            progress_bar.progress(100, text=t('succ_done'))
            st.success(t('succ_done'))
            time.sleep(2)
            st.rerun()

# --- ONGLET 2 : VIVIER ---
with tab2:
    st.markdown(f"<h2 style='color: #0F172A; font-weight: 800; font-size: 2rem; margin-bottom: 1rem;'>{t('pool_title')}</h2>", unsafe_allow_html=True)
    
    if offers_df.empty:
        st.info(t('pool_no_camp'))
    else:
        offer_map_vivier = dict(zip(offers_df['title'] + " (" + offers_df['created_at'].str.split().str[0] + ")", offers_df['id']))
        selected_offer_vivier = st.selectbox(t('pool_show'), list(offer_map_vivier.keys()), key="vivier_select")
        filter_offer_id = offer_map_vivier[selected_offer_vivier]
        
        df_history = get_candidates_by_offer(filter_offer_id)
        job_description_vivier = offers_df[offers_df['id'] == filter_offer_id]['description'].iloc[0]
        
        col_title, col_bulk_gen, col_bulk_del, col_export, col_del_offer = st.columns([1, 1.3, 1.3, 1.3, 1.3])
        
        with col_title:
            st.markdown(t('pool_total').format(len(df_history)))
            
        with col_bulk_gen:
            if not df_history.empty:
                if st.button(t('btn_gen'), type="primary", use_container_width=True):
                    selected_rows = [row for idx, row in df_history.iterrows() if st.session_state.get(f"select_cand_{row['id']}", False)]
                    if not selected_rows:
                        st.warning(t('warn_check'))
                    else:
                        progress_bulk = st.progress(0, text=t('prog_init'))
                        for i, row in enumerate(selected_rows):
                            progress_bulk.progress(int((i / len(selected_rows)) * 100), text=t('prog_gen').format(row['nom']))
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
                        
                        progress_bulk.progress(100, text=t('succ_gen'))
                        time.sleep(1)
                        st.rerun()

        with col_bulk_del:
            if not df_history.empty:
                bulk_del_key = f"bulk_del_{filter_offer_id}"
                
                if bulk_del_key not in st.session_state:
                    st.session_state[bulk_del_key] = False
                    
                if not st.session_state[bulk_del_key]:
                    if st.button(t('btn_del_sel'), type="primary", use_container_width=True):
                        selected_rows = [row['id'] for idx, row in df_history.iterrows() if st.session_state.get(f"select_cand_{row['id']}", False)]
                        if not selected_rows:
                            st.warning(t('warn_check'))
                        else:
                            st.session_state[bulk_del_key] = True
                            st.rerun()
                else:
                    st.error(t('ask_sure'))
                    cY, cN = st.columns(2)
                    with cY:
                        if st.button(t('yes'), type="primary", key="yes_bulk_del"):
                            for cid in [row['id'] for idx, row in df_history.iterrows() if st.session_state.get(f"select_cand_{row['id']}", False)]:
                                delete_candidate(cid)
                            st.session_state[bulk_del_key] = False
                            st.rerun()
                    with cN:
                        if st.button(t('no'), type="secondary", key="no_bulk_del"):
                            st.session_state[bulk_del_key] = False
                            st.rerun()

        with col_export:
            if not df_history.empty:
                offer_title_raw = offers_df[offers_df['id'] == filter_offer_id]['title'].iloc[0]
                clean_title = offer_title_raw.replace(" ", "_").replace("/", "-").replace("\\", "-")
                
                csv_data = prepare_export_df(df_history).to_csv(index=False, sep=';', encoding='utf-8-sig')
                
                st.download_button(
                    label=t('btn_export'), 
                    data=csv_data, 
                    file_name=f"candidats_{clean_title}.csv", 
                    mime="text/csv", 
                    use_container_width=True
                )
                
        with col_del_offer:
            offer_del_key = f"del_offer_{filter_offer_id}"
            
            if offer_del_key not in st.session_state:
                st.session_state[offer_del_key] = False
                
            if not st.session_state[offer_del_key]:
                if st.button(t('btn_del_camp'), type="primary", key=f"btn_{offer_del_key}", use_container_width=True):
                    st.session_state[offer_del_key] = True
                    st.rerun()
            else:
                st.error(t('ask_sure'))
                cY, cN = st.columns(2)
                with cY:
                    if st.button(t('yes'), type="primary", key=f"yes_{offer_del_key}"):
                        delete_job_offer(filter_offer_id)
                        st.session_state[offer_del_key] = False
                        st.rerun()
                with cN:
                    if st.button(t('no'), type="secondary", key=f"no_{offer_del_key}"):
                        st.session_state[offer_del_key] = False
                        st.rerun()

        st.markdown("<hr style='border-color: #E2E8F0; margin: 10px 0;'>", unsafe_allow_html=True)

        if df_history.empty:
            st.info(t('pool_no_cand'))
        else:
            max_cands = len(df_history)
            
            if "applied_top_n" not in st.session_state:
                st.session_state.applied_top_n = min(5, max_cands)
            if st.session_state.applied_top_n > max_cands and max_cands > 0:
                st.session_state.applied_top_n = max_cands
                
            if "applied_sort" not in st.session_state:
                st.session_state.applied_sort = t('sort_desc')
                
            sort_options = [t('sort_desc'), t('sort_asc'), t('sort_az')]

            st.markdown(f"<div style='margin-bottom: 10px; font-weight: 600; color: #475569;'>{t('filt_title')}</div>", unsafe_allow_html=True)
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                with st.form(key="form_top_n", border=True):
                    new_top_n = st.number_input(t('filt_top'), 1, max_cands, st.session_state.applied_top_n, 1)
                    if st.form_submit_button(t('btn_apply'), type="secondary"):
                        st.session_state.applied_top_n = new_top_n
                        st.rerun()
                        
            with col_f2:
                with st.form(key="form_sort", border=True):
                    new_sort = st.selectbox(t('filt_sort'), sort_options, index=sort_options.index(st.session_state.applied_sort) if st.session_state.applied_sort in sort_options else 0)
                    if st.form_submit_button(t('btn_apply'), type="secondary"):
                        st.session_state.applied_sort = new_sort
                        st.rerun()

            df_top = df_history.nlargest(st.session_state.applied_top_n, 'score_final')
            
            if st.session_state.applied_sort == t('sort_desc'):
                df_display = df_top.sort_values(by='score_final', ascending=False)
            elif st.session_state.applied_sort == t('sort_asc'):
                df_display = df_top.sort_values(by='score_final', ascending=True)
            else:
                df_display = df_top.sort_values(by='nom', ascending=True)

            if df_display.empty:
                st.warning(t('warn_empty'))
            else:
                all_selected = True
                for idx, row in df_display.iterrows():
                    if not st.session_state.get(f"select_cand_{row['id']}", False):
                        all_selected = False
                        break
                
                master_val = st.checkbox(t('chk_all').format(len(df_display)), value=all_selected)
                if master_val != all_selected:
                    for idx, row in df_display.iterrows():
                        st.session_state[f"select_cand_{row['id']}"] = master_val
                    st.rerun()
                
                for idx, row in df_display.iterrows():
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
                                <div style='font-size: 0.85rem; color: #475569; margin-top: 4px;'><b>{t('scanned_on')}</b> {row['date_scan']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander(t('exp_see').format(row['nom'])):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.markdown(t('exp_proof').format(cand_data.get('preuve_ingenierie', 'Non précisé')))
                                st.markdown(f"{t('exp_strength')} <span style='color:#10B981;'>{cand_data.get('strength', '-')}</span>", unsafe_allow_html=True)
                                st.markdown(f"{t('exp_risk')} <span style='color:#EF4444;'>{cand_data.get('risk', '-')}</span>", unsafe_allow_html=True)
                                st.markdown(f"{t('exp_conc')} {cand_data.get('reasoning', '')}")
                            with col2:
                                st.plotly_chart(create_radar_chart(cand_data), use_container_width=True, config={'displayModeBar': False}, key=f"hist_radar_{row['id']}")
                            
                            st.markdown("<hr style='border-color: #E2E8F0; margin: 15px 0;'>", unsafe_allow_html=True)
                            
                            q_data = cand_data.get("interview_questions")
                            if not q_data and score > 0:
                                st.markdown(f"<div style='padding:10px; color:#64748B; font-style:italic;'>{t('exp_no_q')}</div>", unsafe_allow_html=True)
                            elif q_data:
                                st.markdown("<div style='background-color:#F8FAFC; padding:15px; border-radius:8px; border:1px solid #E2E8F0;'>", unsafe_allow_html=True)
                                st.markdown(t('exp_q_title'))
                                for key in ["q1_force", "q2_risque", "q3_situation"]:
                                    if key in q_data:
                                        st.markdown(f"**{q_data[key].get('titre', '')}**")
                                        st.markdown(f"*« {q_data[key].get('question', '')} »*")
                                        st.markdown(f"{t('exp_expect')} {q_data[key].get('attente', '')}<br>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            cand_del_key = f"del_cand_{row['id']}"
                            if cand_del_key not in st.session_state:
                                st.session_state[cand_del_key] = False
                                
                            if not st.session_state[cand_del_key]:
                                if st.button(t('btn_del_cand'), type="secondary", key=f"btn_{cand_del_key}"):
                                    st.session_state[cand_del_key] = True
                                    st.rerun()
                            else:
                                st.warning(t('ask_sure'))
                                cY, cN = st.columns([1, 1])
                                with cY:
                                    if st.button(t('yes'), type="primary", key=f"yes_{cand_del_key}"):
                                        delete_candidate(row['id'])
                                        st.session_state[cand_del_key] = False
                                        st.rerun()
                                with cN:
                                    if st.button(t('no'), type="secondary", key=f"no_{cand_del_key}"):
                                        st.session_state[cand_del_key] = False
                                        st.rerun()