import pandas as pd
import random
import datetime

# --- CONFIGURATION DES DONNÉES ---
FIRST_NAMES = ["Lucas", "Sarah", "Julie", "Marc", "Thomas", "Emma", "Léa", "Pierre", "Paul", "Jacques", "Marie", "Sophie", "Kevin", "Ahmed", "Fatima", "Yuki", "John", "Jane", "Roberto", "Chloé"]
LAST_NAMES = ["Dubois", "Martin", "Petit", "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefevre", "Michel", "Garcia", "David", "Bertrand", "Roux", "Vincent"]
DOMAINS = ["gmail.com", "yahoo.fr", "hotmail.com", "outlook.com", "orange.fr", "fake.db"]

TECH_SKILLS = ["Python", "SQL", "React", "Java", "C++", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Pandas", "Airflow", "Terraform", "Excel", "VBA"]
TRAP_SKILLS = ["Cuisine", "Jardinage", "Mario Kart", "Sommeil", "Minecraft", "Netflix", "Rien", "Word 97", "Paint"]
LEVELS = ["Junior", "Senior", "Expert", "Stagiaire", "Lead"]

# --- FONCTIONS DE GÉNÉRATION ---

def get_random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def get_random_email(name):
    # Piège : Parfois pas d'email, ou format invalide
    if random.random() < 0.05: return None # 5% de chance d'être vide
    if random.random() < 0.05: return "pas d'email" # 5% de format pourri
    
    clean_name = name.lower().replace(" ", ".")
    return f"{clean_name}@{random.choice(DOMAINS)}"

def get_random_exp():
    # Piège : Mélange de int, float, et string
    rand = random.random()
    if rand < 0.1: return "dix ans" # Piège textuel
    if rand < 0.2: return "N/A" # Piège vide
    if rand < 0.3: return -5 # Piège négatif
    if rand < 0.4: return 0.5 # Float
    return random.randint(0, 15) # Cas normal

def get_random_skills():
    # Piège : Parfois vide, parfois absurde
    if random.random() < 0.1: return "" # Vide
    
    nb_skills = random.randint(1, 6)
    # Mélange tech et pièges
    pool = TECH_SKILLS + TRAP_SKILLS if random.random() < 0.3 else TECH_SKILLS
    selected = random.sample(pool, min(nb_skills, len(pool)))
    return ", ".join(selected)

def get_random_availability():
    # Piège : Dates passées, formats textes, ou vide
    rand = random.random()
    if rand < 0.4: return "Immédiat"
    if rand < 0.6: return (datetime.date.today() + datetime.timedelta(days=random.randint(10, 90))).strftime("%Y-%m-%d")
    if rand < 0.8: return "Dans 3 mois" # Texte
    if rand < 0.9: return "Hier" # Passé
    return None # Vide

# --- GÉNÉRATION DU DATASET ---
data = []
for _ in range(100):
    name = get_random_name()
    row = {
        "nom": name,
        "email": get_random_email(name),
        "années_exp": get_random_exp(),
        "compétences": get_random_skills(),
        "disponibilité": get_random_availability()
    }
    data.append(row)

# Création DataFrame
df = pd.DataFrame(data)

# Sauvegarde
filename = "data/candidats_100_random.xlsx"
# On s'assure que le dossier data existe
import os
os.makedirs("data", exist_ok=True)

# On écrit aussi un onglet _CONFIG pour que ton pipeline marche direct
with pd.ExcelWriter(filename) as writer:
    df.to_excel(writer, sheet_name="Candidats", index=False)
    
    # Config simple
    config_data = {
        "Key": ["required_skills", "min_years_exp", "worksheet_target"],
        "Value": ["Python, SQL, AWS", "2", "Candidats"]
    }
    pd.DataFrame(config_data).to_excel(writer, sheet_name="_CONFIG", index=False, header=False)

print(f"✅ Fichier généré avec succès : {filename}")
print("📊 Contient 100 lignes avec des pièges (dates, formats, vides, etc.)")