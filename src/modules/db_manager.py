import sqlite3
import pandas as pd
import hashlib
import json

DB_PATH = "talent_db.sqlite"

# --- SECURITÉ : Hachage des mots de passe ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. NOUVELLE TABLE : Les Utilisateurs
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            company_name TEXT NOT NULL
        )
    ''')
    
    # 2. TABLE MODIFIÉE : Les offres (reliées à un utilisateur)
    c.execute('''
        CREATE TABLE IF NOT EXISTS job_offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 3. TABLE DES CANDIDATS (inchangée, mais indirectement protégée via l'offre)
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_id INTEGER,
            nom TEXT NOT NULL,
            titre_profil TEXT,
            score_final INTEGER,
            analyse_json TEXT,
            date_scan TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(offer_id) REFERENCES job_offers(id)
        )
    ''')
    conn.commit()
    conn.close()

# --- GESTION DES UTILISATEURS ---
def create_user(username, password, company_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password_hash, company_name) VALUES (?, ?, ?)',
                  (username, hash_password(password), company_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # L'utilisateur existe déjà
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, company_name FROM users WHERE username = ? AND password_hash = ?', 
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user # Renvoie (id, company_name) si ok, sinon None

# --- GESTION DES OFFRES & CANDIDATS (Filtrés par utilisateur) ---
def create_job_offer(title, description, user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO job_offers (title, description, user_id) VALUES (?, ?, ?)', (title, description, user_id))
    offer_id = c.lastrowid
    conn.commit()
    conn.close()
    return offer_id

def get_all_job_offers(user_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('SELECT * FROM job_offers WHERE user_id = ? ORDER BY created_at DESC', conn, params=(user_id,))
    conn.close()
    return df

def save_candidate(candidate_data, offer_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO candidates (offer_id, nom, titre_profil, score_final, analyse_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        offer_id,
        candidate_data.get('nom', 'Inconnu'),
        candidate_data.get('titre_profil', 'Non spécifié'),
        candidate_data.get('score_final', 0),
        json.dumps(candidate_data)
    ))
    conn.commit()
    conn.close()

def get_candidates_by_offer(offer_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('SELECT * FROM candidates WHERE offer_id = ? ORDER BY score_final DESC', conn, params=(offer_id,))
    conn.close()
    return df

def delete_candidate(candidate_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM candidates WHERE id = ?', (candidate_id,))
    conn.commit()
    conn.close()

def delete_job_offer(offer_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM candidates WHERE offer_id = ?', (offer_id,))
    c.execute('DELETE FROM job_offers WHERE id = ?', (offer_id,))
    conn.commit()
    conn.close()

def update_candidate_data(candidate_id, new_data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE candidates SET analyse_json = ? WHERE id = ?', (json.dumps(new_data), candidate_id))
    conn.commit()
    conn.close()