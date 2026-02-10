import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v7.5 : Force Brute.
    Élimine tous les filtres de rejet pour garantir l'archivage de Monsieur Sezer.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Sensibilité Maximale) ---
        keywords = ["ans", "âge", "aime", "chocolat", "frère", "bedran", "zilan", "boran", "sezer"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Directif) ---
        tree_prompt = f"""
        Donnée : "{prompt}"
        RÈGLES :
        - Boran -> Archives/Utilisateur/Identite/Age ou Archives/Utilisateur/Gouts/Alimentaire
        - Bedran -> Archives/Social/Famille/Bedran/Age ou Archives/Social/Famille/Bedran/Gouts
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Boran a 17 ans", "path": "Archives/Utilisateur/Identite/Age"}} ] }}
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

        # --- SAUVEGARDE SANS FILTRE ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # Aucune condition de rejet ici pour maximiser la réussite [cite: 2026-02-10]
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Erreur de format JSON."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
