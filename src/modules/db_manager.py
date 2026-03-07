# Fichier : src/modules/db_manager.py
import sqlite3
import pandas as pd
import json
from datetime import datetime

DB_NAME = 'talent_ai.db'

def init_db():
    """Initialise la BDD et exécute les MIGRATIONS AUTOMATIQUES sans perte de données."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Création de la table des campagnes
    c.execute('''
        CREATE TABLE IF NOT EXISTS job_offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            title TEXT,
            description TEXT
        )
    ''')
    
    # 2. Création de la table des candidats (Version basique pour accepter l'existant)
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_scan TEXT,
            nom TEXT,
            titre_profil TEXT,
            score_final INTEGER,
            analyse_json TEXT
        )
    ''')
    
    # 3. SYSTÈME DE MIGRATION : On vérifie si la base est à jour
    c.execute("PRAGMA table_info(candidates)")
    columns = [info[1] for info in c.fetchall()]
    
    if 'offer_id' not in columns:
        print("Mise à jour BDD détectée : Ajout de la colonne 'offer_id'...")
        # On ajoute la colonne sans supprimer la table
        c.execute("ALTER TABLE candidates ADD COLUMN offer_id INTEGER")
        
        # On crée une campagne "Archive" pour sauver les anciens CV
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO job_offers (created_at, title, description) VALUES (?, ?, ?)", 
                  (date_now, "Anciens Scans (Archive)", "Candidats scannés avant la mise à jour du système de campagnes."))
        archive_id = c.lastrowid
        
        # On relie tous les anciens CV (qui n'avaient pas d'offre) à cette Archive
        c.execute("UPDATE candidates SET offer_id = ?", (archive_id,))
        print("Migration terminée : Vos anciens CV ont été sauvés dans la campagne 'Archive'.")
        
    conn.commit()
    conn.close()

def create_job_offer(title, description):
    """Crée une nouvelle campagne et retourne son ID."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO job_offers (created_at, title, description) VALUES (?, ?, ?)', (created_at, title, description))
    offer_id = c.lastrowid
    conn.commit()
    conn.close()
    return offer_id

def get_all_job_offers():
    """Récupère la liste de toutes les campagnes."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM job_offers ORDER BY id DESC", conn)
    conn.close()
    return df

def save_candidate(data, offer_id):
    """Sauvegarde un candidat en le liant à une campagne précise."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date_scan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO candidates (offer_id, date_scan, nom, titre_profil, score_final, analyse_json) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        offer_id, 
        date_scan, 
        data.get('nom', 'Inconnu'), 
        data.get('titre_profil', ''), 
        int(data.get('score_final', 0)), 
        json.dumps(data)
    ))
    conn.commit()
    conn.close()

def get_candidates_by_offer(offer_id):
    """Récupère tous les candidats d'une campagne spécifique."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM candidates WHERE offer_id=? ORDER BY score_final DESC", conn, params=(offer_id,))
    conn.close()
    return df

def delete_candidate(cand_id):
    """Supprime un candidat seul."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM candidates WHERE id=?", (cand_id,))
    conn.commit()
    conn.close()

def delete_job_offer(offer_id):
    """Supprime une campagne entière ET tous ses candidats associés."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM candidates WHERE offer_id=?", (offer_id,))
    c.execute("DELETE FROM job_offers WHERE id=?", (offer_id,))
    conn.commit()
    conn.close()