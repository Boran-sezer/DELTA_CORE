import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v7.4 : Archivage Omniscient.
    Élimine les rejets pour une capture fluide des données de Monsieur Sezer.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Souplesse Maximale) ---
        keywords = ["ans", "âge", "aime", "chocolat", "frère", "bedran", "zilan", "boran", "sezer"]
        # On force l'archivage si un mot-clé est présent, peu importe la structure [cite: 2026-02-10]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Chemins Autorisés) ---
        tree_prompt = f"""
        Donnée : "{prompt}"
        RÈGLES :
        1. Monsieur Sezer (Boran) -> Archives/Utilisateur/Identite/Age ou /Gouts/Alimentaire
        2. Tiers (Bedran/Zilan) -> Archives/Social/Famille/[Nom]/Age ou /Gouts
        
        JSON : {{ "fragments": [ {{"content": "Boran a 17 ans", "path": "Archives/Utilisateur/Identite/Age"}} ] }}
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
            
            # On accepte tout chemin commençant par Archives/ pour éviter le blocage [cite: 2026-02-10]
            if not path.startswith("Archives/"):
                continue
                
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée (format invalide)."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
