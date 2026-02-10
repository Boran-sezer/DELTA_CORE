import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v7.8 : Jarvis Ultimate.
    Optimisé pour la clarté des archives de Monsieur Sezer (Boran).
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : FILTRE DE PERTINENCE ---
        keywords = ["ans", "âge", "aime", "chocolat", "frère", "sœur", "pardon", "bedran", "zilan"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : CARTOGRAPHIE CHIRURGICALE ---
        tree_prompt = f"""
        Donnée : "{prompt}"
        CONSIGNE : 
        1. Sujet = Boran (Utilisateur) ou Bedran/Zilan (Social).
        2. Si c'est une correction ("pardon", "non"), remplace l'ancien fait par le nouveau.
        3. Formate le contenu de l'archive de manière factuelle.
        
        STRUCTURE JSON :
        {{ "fragments": [ {{"content": "Boran aime désormais le chocolat au lait", "path": "Archives/Utilisateur/Gouts/Alimentaire"}} ] }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": tree_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        data = json.loads(chat_completion.choices[0].message.content)
        fragments = data.get("fragments", [])[:1] # On garde la limite de 1 pour la précision
        results = []

        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # Sauvegarde directe sans filtres bloquants
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
