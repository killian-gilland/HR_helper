"""
Recruitment Analyst - ÉDITION REFACTORED + NAVIGATION ROBUSTE + UI ÉPURÉE
Code propre, modulaire, prêt pour la mise en production.
"""
import streamlit as st
import json
import logging
import os
import sys
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Talent AI | Enterprise Sourcing", 
    page_icon="🧿", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.modules.utils import extract_text_from_pdf, prepare_export_df
    from src.modules.db_manager import (init_db, create_user, verify_user, create_job_offer, get_all_job_offers, save_candidate, get_candidates_by_offer, delete_candidate, delete_job_offer, update_candidate_data)
    from src.modules.scoring_engine import process_cv_scoring
    from src.modules.interview_generator import generate_interview_questions
    from src.modules.ui_components import create_radar_chart
    from src.modules.translations import t
except ImportError as e:
    st.error(f"Erreur d'import : {e}. Assurez-vous que l'architecture des dossiers est respectée.")
    st.stop()

logging.basicConfig(level=logging.INFO)
init_db()

# ==================== INJECTION DU CSS (DESIGN SAAS ÉPURÉ) ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif !important;}
    .stApp {background-color: #F8FAFC !important;}
    #MainMenu, footer {display: none !important;} 
    
    header {background-color: transparent !important;}
    .block-container {padding-top: 4.5rem !important; max-width: 1400px !important;}
    
    [data-testid="stSidebar"] { background-color: #0B1120 !important; border-right: 1px solid #1E293B !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { color: #F8FAFC !important; }
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea, [data-testid="stSidebar"] select { background-color: #1E293B !important; color: #FFFFFF !important; border: 1px solid #475569 !important; border-radius: 8px !important; }
    [data-testid="stSidebar"] input::placeholder, [data-testid="stSidebar"] textarea::placeholder { color: #94A3B8 !important; opacity: 0.8 !important; }

    [data-testid="stFileUploadDropzone"] { background-color: #0F172A !important; border: 2px dashed #475569 !important; border-radius: 8px !important; }
    [data-testid="stFileUploadDropzone"] *, [data-testid="stFileUploadDropzone"] svg { color: #F8FAFC !important; fill: #F8FAFC !important; }
    
    /* BOUTONS PRINCIPAUX */
    button[kind="primary"], [data-testid="stDownloadButton"] button, [data-testid="stFileUploader"] button { 
        background-color: #1E293B !important; color: #FFFFFF !important; font-weight: 600 !important; font-size: 0.7rem !important;
        border-radius: 6px !important; border: 1px solid #0F172A !important; padding: 0.4rem 0.8rem !important; text-transform: uppercase; 
        transition: background-color 0.2s, transform 0.1s; min-height: 38px !important; display: flex !important;
        align-items: center !important; justify-content: center !important; text-align: center !important; width: 100% !important;
    }
    button[kind="primary"]:hover, [data-testid="stDownloadButton"] button:hover { background-color: #0F172A !important; transform: translateY(-1px); }
    button[kind="primary"]:active { border-color: #EF4444 !important; } 
    
    /* BOUTONS SECONDAIRES */
    button[kind="secondary"] {
        background: transparent !important; color: #64748B !important; font-weight: 600 !important; font-size: 0.7rem !important; 
        border-radius: 6px !important; border: 1px solid transparent !important; padding: 0.4rem 0.8rem !important; text-transform: uppercase !important; 
        transition: all 0.2s; min-height: 38px !important; display: flex !important;
        align-items: center !important; justify-content: center !important; text-align: center !important; width: 100% !important; box-shadow: none !important;
    }
    button[kind="secondary"]:hover { color: #0F172A !important; background-color: #F1F5F9 !important; border-color: #E2E8F0 !important;}

    [data-testid="stFormSubmitButton"] button {
        background-color: #F1F5F9 !important; color: #475569 !important; border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important; padding: 0.2rem 0.8rem !important; font-size: 0.7rem !important;
        font-weight: 600 !important; text-transform: uppercase !important; min-height: 32px !important;
        width: auto !important; box-shadow: none !important;
    }
    [data-testid="stFormSubmitButton"] button:hover { background-color: #E2E8F0 !important; color: #0F172A !important; border-color: #94A3B8 !important; }

    .lang-btn button, .lang-btn button p, .lang-btn button span { font-size: 3.5rem !important; margin: 0 !important; padding: 0 !important;}
    .lang-btn button { background: transparent !important; border: none !important; min-height: 0 !important; padding: 0 !important; width: auto !important; transition: transform 0.2s;}
    .lang-btn button:hover { transform: scale(1.1); background: transparent !important; border: none !important;}

    /* FUSION CARTE / ACCORDÉON */
    [data-testid="stExpander"] {
        background: white !important;
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 5px !important;
    }
    [data-testid="stExpander"] summary { padding: 10px 15px !important; }
    [data-testid="stExpander"] summary:hover { background-color: #F8FAFC !important; }
    [data-testid="stExpander"] summary p { font-size: 1.1rem !important; font-weight: 700 !important; color: #0F172A !important; }
</style>
""", unsafe_allow_html=True)

# ==================== SÉLECTEUR DE LANGUE ====================
if 'lang' not in st.session_state:
    st.session_state.lang = 'fr'

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

if not st.session_state.logged_in:
    st.markdown("<style>.block-container {padding-top: 1rem !important;}</style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #0F172A;'>TALENT<span style='color: #3B82F6;'>.AI</span></h1><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["Connexion" if st.session_state.lang == 'fr' else "Log In", "Créer un compte" if st.session_state.lang == 'fr' else "Sign Up"])
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
                    if create_user(reg_user, reg_pass, reg_comp):
                        st.success(t('succ_acct'))
                    else: st.error(t('err_exist'))
                else: st.warning(t('err_fill'))
    st.stop()

# ==================== INTERFACE SAAS PRINCIPALE ====================

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: white; font-weight: 900; font-size: 1.8rem; margin-bottom: 0;'>TALENT<span style='color: #3B82F6;'>.AI</span></h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #10B981; font-size: 0.8rem; font-weight: 700; margin-top: 5px; margin-bottom: 30px;'>🟢 ESPACE : {st.session_state.company_name.upper()}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>{t('sb_step1')}</p>", unsafe_allow_html=True)
    
    offers_df = get_all_job_offers(st.session_state.user_id)
    offer_mode = st.radio(t('sb_mode'), [t('sb_new_offer'), t('sb_old_offer')], label_visibility="collapsed")
    current_offer_id, job_description, offer_title = None, "", ""
    
    if offer_mode == t('sb_new_offer'):
        offer_title = st.text_input(t('sb_title'), placeholder="Lead Data Scientist")
        job_description = st.text_area(t('sb_desc'), height=150)
    else:
        if offers_df.empty: st.warning(t('sb_no_camp'))
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
    if 'confirm_logout' not in st.session_state: st.session_state.confirm_logout = False

    if not st.session_state.confirm_logout:
        if st.button(t('btn_logout'), type="secondary"):
            st.session_state.confirm_logout = True
            st.rerun()
    else:
        st.warning(t('ask_sure'))
        c_yes, c_no = st.columns(2)
        with c_yes:
            if st.button(t('yes'), type="primary", key="btn_yes_log"): logout()
        with c_no:
            if st.button(t('no'), type="secondary", key="btn_no_log"): st.session_state.confirm_logout = False; st.rerun()

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'scan'

col_nav1, col_nav2, col_nav3 = st.columns([3, 4, 5])
with col_nav1:
    if st.button(t('tab_scan'), type="primary" if st.session_state.current_page == 'scan' else "secondary", use_container_width=True):
        st.session_state.current_page = 'scan'
        st.rerun()
with col_nav2:
    if st.button(t('tab_pool'), type="primary" if st.session_state.current_page == 'pool' else "secondary", use_container_width=True):
        st.session_state.current_page = 'pool'
        st.rerun()

st.markdown("<hr style='margin-top: 0px; border-color: #E2E8F0;'>", unsafe_allow_html=True)


# --- PAGE 1 : SCAN ---
if st.session_state.current_page == 'scan':
    if not launch_btn:
        st.markdown(f"""
        <div style="padding: 1rem 2rem;">
        <h1 style="color: #0F172A; font-weight: 800; font-size: 2.2rem; margin-bottom: 0.5rem;">{t('hello').format(st.session_state.company_name)}</h1>
        <p style="color: #64748B; font-size: 1.1rem; margin-bottom: 2rem;">{t('hello_sub')}</p>
        </div>
        """, unsafe_allow_html=True)
        if uploaded_files:
            st.info("📄 Documents chargés et prêts pour l'analyse. Cliquez sur le bouton dans le menu.")

    elif launch_btn:
        if not uploaded_files: st.warning(t('warn_no_cv'))
        elif offer_mode == t('sb_new_offer') and (not offer_title or not job_description): st.warning(t('warn_no_title'))
        else:
            if offer_mode == t('sb_new_offer'):
                current_offer_id = create_job_offer(offer_title, job_description, st.session_state.user_id)
                st.success(t('succ_camp').format(offer_title))
            
            progress_bar = st.progress(0, text=t('prog_init'))
            for i, file in enumerate(uploaded_files):
                progress_bar.progress(int((i / len(uploaded_files)) * 100), text=t('prog_scan').format(file.name, i+1, len(uploaded_files)))
                text = extract_text_from_pdf(file)
                if not text or len(text) < 20 or "ERREUR" in text:
                    save_candidate({"nom": file.name, "score_final": 0, "reasoning": t('err_doc')}, current_offer_id)
                else:
                    data = process_cv_scoring(text, job_description)
                    final_score = min(int(data.get("n_hard_skills_coeur",0)), 65) + min(int(data.get("n_outils_metier",0)), 10) + min(int(data.get("n_business_impact",0)), 10) + min(int(data.get("n_seniorite",0)), 5) + min(int(data.get("n_soft_skills",0)), 5) + min(int(data.get("n_storytelling",0)), 5)
                    data.update({"score_final": final_score})
                    save_candidate(data, current_offer_id)
                time.sleep(20)
            
            progress_bar.progress(100, text=t('succ_done'))
            st.success(t('succ_done'))
            time.sleep(2)
            st.session_state.current_page = 'pool'
            st.rerun()

# --- PAGE 2 : VIVIER ---
elif st.session_state.current_page == 'pool':
    st.markdown(f"<h2 style='color: #0F172A; font-weight: 800; font-size: 2rem; margin-bottom: 1rem;'>{t('pool_title')}</h2>", unsafe_allow_html=True)
    
    if offers_df.empty: st.info(t('pool_no_camp'))
    else:
        offer_map_vivier = dict(zip(offers_df['title'] + " (" + offers_df['created_at'].str.split().str[0] + ")", offers_df['id']))
        selected_offer_vivier = st.selectbox(t('pool_show'), list(offer_map_vivier.keys()), key="vivier_select")
        filter_offer_id = offer_map_vivier[selected_offer_vivier]
        
        df_history = get_candidates_by_offer(filter_offer_id)
        job_description_vivier = offers_df[offers_df['id'] == filter_offer_id]['description'].iloc[0]
        
        # ⚡ EVALUATION DES SELECTIONS POUR LES BOUTONS
        selected_rows = [row for _, row in df_history.iterrows() if st.session_state.get(f"select_cand_{row['id']}", False)]
        has_selection = len(selected_rows) > 0
        
        col_title, col_bulk_gen, col_bulk_del, col_export, col_del_offer = st.columns([1, 1.3, 1.3, 1.3, 1.3])
        with col_title: st.markdown(t('pool_total').format(len(df_history)))
            
        with col_bulk_gen:
            if not df_history.empty:
                # Bouton grisé si aucune sélection
                if st.button(t('btn_gen'), type="primary", use_container_width=True, disabled=not has_selection):
                    progress_bulk = st.progress(0, text=t('prog_init'))
                    for i, row in enumerate(selected_rows):
                        progress_bulk.progress(int((i / len(selected_rows)) * 100), text=t('prog_gen').format(row['nom']))
                        try: cand_data = json.loads(row['analyse_json'])
                        except: continue
                        if "interview_questions" not in cand_data and row['score_final'] > 0:
                            questions = generate_interview_questions(cand_data, job_description_vivier)
                            if questions:
                                cand_data["interview_questions"] = questions
                                update_candidate_data(row['id'], cand_data) 
                                time.sleep(2) 
                    progress_bulk.progress(100, text=t('succ_gen'))
                    time.sleep(1); st.rerun()

        with col_bulk_del:
            if not df_history.empty:
                bulk_del_key = f"bulk_del_{filter_offer_id}"
                if bulk_del_key not in st.session_state: st.session_state[bulk_del_key] = False
                
                if not st.session_state[bulk_del_key]:
                    # Bouton grisé si aucune sélection
                    if st.button(t('btn_del_sel'), type="primary", use_container_width=True, disabled=not has_selection):
                        st.session_state[bulk_del_key] = True; st.rerun()
                else:
                    st.error(t('ask_sure'))
                    cY, cN = st.columns(2)
                    with cY:
                        if st.button(t('yes'), type="primary", key="yes_bulk_del"):
                            for row in selected_rows: delete_candidate(row['id'])
                            st.session_state[bulk_del_key] = False; st.rerun()
                    with cN:
                        if st.button(t('no'), type="secondary", key="no_bulk_del"): st.session_state[bulk_del_key] = False; st.rerun()

        with col_export:
            if not df_history.empty:
                clean_title = offers_df[offers_df['id'] == filter_offer_id]['title'].iloc[0].replace(" ", "_").replace("/", "-").replace("\\", "-")
                
                # Bouton grisé si aucune sélection
                if not has_selection:
                    st.download_button(t('btn_export'), "", file_name=f"candidats_{clean_title}.csv", mime="text/csv", use_container_width=True, disabled=True)
                else:
                    selected_ids = [r['id'] for r in selected_rows]
                    df_selected = df_history[df_history['id'].isin(selected_ids)]
                    csv_data = prepare_export_df(df_selected, st.session_state.lang).to_csv(index=False, sep=';', encoding='utf-8-sig')
                    st.download_button(t('btn_export'), csv_data, f"candidats_{clean_title}.csv", "text/csv", use_container_width=True)
                
        with col_del_offer:
            offer_del_key = f"del_offer_{filter_offer_id}"
            if offer_del_key not in st.session_state: st.session_state[offer_del_key] = False
            if not st.session_state[offer_del_key]:
                if st.button(t('btn_del_camp'), type="primary", key=f"btn_{offer_del_key}", use_container_width=True): st.session_state[offer_del_key] = True; st.rerun()
            else:
                st.error(t('ask_sure'))
                cY, cN = st.columns(2)
                with cY:
                    if st.button(t('yes'), type="primary", key=f"yes_{offer_del_key}"): delete_job_offer(filter_offer_id); st.session_state[offer_del_key] = False; st.rerun()
                with cN:
                    if st.button(t('no'), type="secondary", key=f"no_{offer_del_key}"): st.session_state[offer_del_key] = False; st.rerun()

        st.markdown("<hr style='border-color: #E2E8F0; margin: 10px 0;'>", unsafe_allow_html=True)

        if df_history.empty: st.info(t('pool_no_cand'))
        else:
            max_cands = len(df_history)
            if "applied_top_n" not in st.session_state: st.session_state.applied_top_n = min(5, max_cands)
            if st.session_state.applied_top_n > max_cands and max_cands > 0: st.session_state.applied_top_n = max_cands
            
            sort_map = {'desc': t('sort_desc'), 'asc': t('sort_asc'), 'az': t('sort_az')}
            if "applied_sort_id" not in st.session_state: st.session_state.applied_sort_id = 'desc'

            st.markdown(f"<div style='margin-bottom: 10px; font-weight: 600; color: #475569;'>{t('filt_title')}</div>", unsafe_allow_html=True)
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                with st.form(key="form_top_n", border=True):
                    new_top_n = st.number_input(t('filt_top'), 1, max_cands, st.session_state.applied_top_n, 1)
                    if st.form_submit_button(t('btn_apply'), type="secondary"): st.session_state.applied_top_n = new_top_n; st.rerun()
            with col_f2:
                with st.form(key="form_sort", border=True):
                    current_display = sort_map[st.session_state.applied_sort_id]
                    new_sort_display = st.selectbox(t('filt_sort'), list(sort_map.values()), index=list(sort_map.values()).index(current_display))
                    if st.form_submit_button(t('btn_apply'), type="secondary"): 
                        st.session_state.applied_sort_id = {v: k for k, v in sort_map.items()}[new_sort_display]
                        st.rerun()

            df_top = df_history.nlargest(st.session_state.applied_top_n, 'score_final')
            if st.session_state.applied_sort_id == 'desc': df_display = df_top.sort_values(by='score_final', ascending=False)
            elif st.session_state.applied_sort_id == 'asc': df_display = df_top.sort_values(by='score_final', ascending=True)
            else: df_display = df_top.sort_values(by='nom', ascending=True)

            if df_display.empty: st.warning(t('warn_empty'))
            else:
                all_selected = all(st.session_state.get(f"select_cand_{row['id']}", False) for _, row in df_display.iterrows())
                master_val = st.checkbox(t('chk_all').format(len(df_display)), value=all_selected)
                if master_val != all_selected:
                    for _, row in df_display.iterrows(): st.session_state[f"select_cand_{row['id']}"] = master_val
                    st.rerun()
                
                for _, row in df_display.iterrows():
                    score = row['score_final']
                    emoji_score = "🟢" if score >= 60 else ("🟠" if score >= 40 else "🔴")
                    
                    try: cand_data = json.loads(row['analyse_json'])
                    except: cand_data = {}
                    
                    col_chk, col_card = st.columns([0.5, 11.5])
                    with col_chk:
                        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                        st.checkbox(" ", key=f"select_cand_{row['id']}", label_visibility="collapsed")
                        
                    with col_card:
                        expander_label = f"{emoji_score} Score : {score}/100 &nbsp; | &nbsp; {row['nom']} — {row['titre_profil']}"
                        
                        with st.expander(expander_label):
                            st.markdown(f"<div style='font-size: 0.85rem; color: #64748B; margin-bottom: 15px;'><b>{t('scanned_on')}</b> {row['date_scan']}</div>", unsafe_allow_html=True)
                            
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
                            if not q_data and score > 0: st.markdown(f"<div style='padding:10px; color:#64748B; font-style:italic;'>{t('exp_no_q')}</div>", unsafe_allow_html=True)
                            elif q_data:
                                st.markdown("<div style='background-color:#F8FAFC; padding:15px; border-radius:8px; border:1px solid #E2E8F0;'>", unsafe_allow_html=True)
                                st.markdown(t('exp_q_title'))
                                for key in ["q1_force", "q2_risque", "q3_situation"]:
                                    if key in q_data:
                                        st.markdown(f"**{q_data[key].get('titre', '')}**\n*« {q_data[key].get('question', '')} »*\n{t('exp_expect')} {q_data[key].get('attente', '')}<br>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            cand_del_key = f"del_cand_{row['id']}"
                            if cand_del_key not in st.session_state: st.session_state[cand_del_key] = False
                            if not st.session_state[cand_del_key]:
                                if st.button(t('btn_del_cand'), type="secondary", key=f"btn_{cand_del_key}"): st.session_state[cand_del_key] = True; st.rerun()
                            else:
                                st.warning(t('ask_sure'))
                                cY, cN = st.columns([1, 1])
                                with cY:
                                    if st.button(t('yes'), type="primary", key=f"yes_{cand_del_key}"): delete_candidate(row['id']); st.session_state[cand_del_key] = False; st.rerun()
                                with cN:
                                    if st.button(t('no'), type="secondary", key=f"no_{cand_del_key}"): st.session_state[cand_del_key] = False; st.rerun()