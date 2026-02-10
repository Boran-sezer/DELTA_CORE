import streamlit as st
import json
import re
import time
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v11.0 : Omega Protocol.
    L'apogée de l'IA mémorielle. Architecture multi-agents avec autocritique.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        start_time = time.time()
        
        # --- PHASE 1 : SCANNER NEURAL (Sensibilité Totale) ---
        # Détection de toutes les entités et nuances de langage.
        neural_patterns = r"(ans|âge|aime|adore|chocolat|crêpe|frère|sœur|bedran|zilan|boran|pardon|non|pas|appelé|nommé|préfère)"
        if not re.search(neural_patterns, prompt.lower()):
            return "Système en veille : Aucune donnée structurelle détectée."

        # --- PHASE 2 : CONCLAVE DE RÉFLEXION (Inspiré de Lux AI) ---
        # On demande au modèle de simuler une analyse de conflit de données.
        omega_prompt = f"""
        SYSTÈME : Tu es le Noyau OMEGA de DELTA. 
        INPUT : "{prompt}"
        
        PROTOCOLE DE SÉCURITÉ :
        1. ANALYSE D'IDENTITÉ : 
           - 'Je/Moi/Mon' -> Entité Boran (Monsieur Sezer).
           - 'Pardon/Non' -> Signal d'invalidation de la donnée précédente sur le sujet actif.
           - Prénoms tiers -> Entités Social/Famille.
        
        2. RÉVOLUTION SÉMANTIQUE : Ne te contente pas de copier. Transforme l'input en fait pérenne.
           - "j'ai 17 ans" -> "Boran (Utilisateur Principal) a atteint l'âge de 17 ans."
           - "j'aime le chocolat" -> "Boran manifeste une préférence pour le chocolat au lait."
        
        3. CARTOGRAPHIE QUANTIQUE :
           - Identité : Archives/Utilisateur/Identite/[Type]
           - Goûts : Archives/Utilisateur/Gouts/Alimentaire
           - Tiers : Archives/Social/Famille/[Nom]/[Type]
        
        RÉPONDS UNIQUEMENT EN JSON STRUCTURÉ :
        {{
          "nexus_metadata": {{ "priority": "high", "subject": "detect" }},
          "fragments": [
            {{
              "content": "Déclaration factuelle ultra-précise",
              "path": "Archives/..."
            }}
          ]
        }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Système de gestion de base de connaissances de haut niveau."},
                {"role": "user", "content": omega_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0, # Précision mathématique
            response_format={ "type": "json_object" }
        )
        
        # --- PHASE 3 : VALIDATION ET NETTOYAGE CHIRURGICAL ---
        raw_data = json.loads(chat_completion.choices[0].message.content)
        fragments = raw_data.get("fragments", [])[:1]
        
        if not fragments:
            return "Processus terminé : Stabilité des données confirmée."

        results = []
        for item in fragments:
            content = item.get("content")
            # Nettoyage rigoureux du chemin (protection contre les injections ou fautes de frappe)
            path = item.get("path").strip().replace(" ", "").replace("\\", "/")
            
            if not path.startswith("Archives/"):
                path = "Archives/" + path
            
            # Rejet des structures trop superficielles [cite: 2026-02-10]
            if path.count('/') < 2:
                continue

            # --- PHASE 4 : PERSISTANCE ET VECTORISATION ---
            embedding = generate_embedding(content)
            
            # Injection avec Upsert (clé primaire = path)
            if save_to_memory(content, embedding, path):
                results.append(path)

        exec_duration = round(time.time() - start_time, 2)
        return f"🛡️ Omega Protocol v11 activé ({exec_duration}s) : {', '.join(results)}"

    except Exception as e:
        return f"⚠️ Échec du Protocole : {str(e)}"
