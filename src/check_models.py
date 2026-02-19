import os
import google.generativeai as genai
from dotenv import load_dotenv

# Charge la clé
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERREUR: Pas de clé GEMINI_API_KEY trouvée dans le .env")
else:
    print(f"✅ Clé trouvée: {api_key[:10]}...")
    
    # Configure Google
    genai.configure(api_key=api_key)
    
    print("\n🔍 Interrogation de Google pour voir les modèles disponibles...")
    try:
        count = 0
        for m in genai.list_models():
            # On cherche uniquement les modèles qui peuvent générer du texte (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                print(f"   👉 Modèle disponible : {m.name}")
                count += 1
        
        if count == 0:
            print("⚠️ Aucun modèle de génération de texte trouvé. Vérifie ton compte Google AI Studio.")
        else:
            print(f"\n✅ Succès ! Tu as accès à {count} modèles.")
            
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE : {e}")