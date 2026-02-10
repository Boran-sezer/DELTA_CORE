import streamlit as st
import json
import re
import time
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v10.0 : Jarvis Sentience (Version Maximale).
    Inspiré par Lux AI, Auto-GPT et la gestion de mémoire par graphes.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        start_time = time.time()
        
        # --- ÉTAPE 1 : SCANNER D'INTENTION MULTI-COUCHES ---
        # Détection étendue des entités, goûts, âges et corrections sémantiques.
        patterns = [
            r"(ans|âge|né|anniversaire)", r"(aime|adore|préfère|déteste|goût)", 
            r"(frère|sœur|père|mère|famille)", r"(non|pardon|faux|trompé|erreur|rectification)",
            r"(bedran|zilan|boran|sezer)"
        ]
        if not any(re.search(p, prompt.lower()) for p in patterns):
            return "Interaction simple (aucune donnée structurelle détectée)"

        # --- ÉTAPE 2 : LE CONCLAVE DES AGENTS (Lux AI Logic) ---
        # On force l'IA à jouer trois rôles pour une précision de 100% [cite: 2026-02-10]
        reasoning_prompt = f"""
        SYSTÈME : Tu es le Nexus v10.0 de DELTA. Donnée : "{prompt}"
        
        MISSION : Analyser, classifier et sécuriser l'information de Monsieur Sezer.
        
        PHASE 1 - ANALYSE : Identifie le sujet. 
        - 'Moi/Je/Boran' -> Utilisateur Principal.
        - 'Bedran/Zilan/Tiers' -> Social/Famille.
        - 'Pardon/Non' -> Signal de mise à jour (Upsert) sur le sujet précédent.
        
        PHASE 2 - CHEMINS : 
        - Archives/Utilisateur/Identite/Age
        - Archives/Utilisateur/Gouts/Alimentaire
        - Archives/Social/Famille/[Nom]/Age
        - Archives/Social/Famille/[Nom]/Gouts
        
        PHASE 3 - RÉDACTION : Le contenu doit être une déclaration factuelle.
        Exemple : "Boran possède désormais une préférence pour le chocolat au lait".
        
        RÉPONDS UNIQUEMENT EN JSON VALIDE :
        {{
          "metadata": {{ "confidence": 1.0, "subject": "Boran" }},
          "fragments": [
            {{
              "content": "Déclaration complète et précise",
              "path": "Archives/..."
            }}
          ]
        }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": "Assistant de gestion mémoire type Lux AI."},
                      {"role": "user", "content": reasoning_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1, # Un soupçon de nuance, mais reste précis
            response_format={ "type": "json_object" }
        )
        
        # --- ÉTAPE 3 : PARSING ET SÉCURISATION ---
        response_data = json.loads(chat_completion.choices[0].message.content)
        fragments = response_data.get("fragments", [])[:1]
        
        if not fragments:
            return "Analyse terminée : Aucune mutation nécessaire."

        # --- ÉTAPE 4 : PERSISTANCE VECTORIELLE ---
        results = []
        for item in fragments:
            content = item.get("content")
            path = item.get("path").strip().replace(" ", "")
            
            # Correction automatique du préfixe de chemin [cite: 2026-02-10]
            if not path.startswith("Archives/"):
                path = "Archives/" + path
            
            # Éjection des chemins trop courts/invalides
            if path.count('/') < 2:
                continue

            # Génération de l'empreinte sémantique (Embedding)
            embedding = generate_embedding(content)
            
            # Injection dans Supabase avec écrasement intelligent (Upsert)
            if save_to_memory(content, embedding, path):
                results.append(path)

        execution_time = round(time.time() - start_time, 2)
        return f"🛡️ Nexus v10 mis à jour en {execution_time}s : {', '.join(results)}"

    except Exception as e:
        return f"⚠️ Alerte Critique Système : {str(e)}"
