import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v7.1 : Jarvis Core.
    Optimisé pour Monsieur Sezer : mémorisation instantanée et précise.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Capture Totale) ---
        keywords = ["ans", "âge", "aime", "chocolat", "crêpe", "plat", "pardon", "bedran", "zilan", "boran"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Chemins Fixes) ---
        # On impose des chemins précis pour éviter les rejets [cite: 2026-02-10]
        tree_prompt = f"""
        Donnée : "{prompt}"
        RÈGLES DE CHEMINS :
        - Monsieur Sezer -> Archives/Utilisateur/Identite/Age OU Archives/Utilisateur/Gouts/Alimentaire
        - Bedran -> Archives/Social/Famille/Bedran/Age OU Archives/Social/Famille/Bedran/Gouts
        
        JSON OBLIGATOIRE :
        {{ "fragments": [ {{"content": "Sujet + info précise", "path": "Le chemin complet"}} ] }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": tree_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        data = json.loads(chat_completion.choices[0].message.content)
        fragments = data.get("fragments", [])[:2]
        results = []

        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # Validation simplifiée : on accepte tout chemin structuré [cite: 2026-02-10]
            if not path.startswith("Archives/"):
                continue
                
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée (format invalide)."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
