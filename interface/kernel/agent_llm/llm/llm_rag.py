import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v7.7 : Protocol Jarvis.
    Verrouillage strict des sujets pour empêcher les mélanges Boran/Bedran.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : DÉTECTION ---
        keywords = ["ans", "âge", "aime", "chocolat", "frère", "bedran", "zilan", "boran", "pardon"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : CARTOGRAPHIE SÉLECTIVE ---
        # On force l'IA à choisir UN SEUL chemin par fait pour éviter les doublons [cite: 2026-02-10]
        tree_prompt = f"""
        Donnée : "{prompt}"
        RÈGLE DE SÉPARATION :
        1. Si l'utilisateur parle de lui (Je/Moi/Pardon) -> Archives/Utilisateur/Gouts/Alimentaire
        2. Si l'utilisateur parle de son frère (Lui/Bedran) -> Archives/Social/Famille/Bedran/Gouts
        
        IMPORTANT : Ne crée jamais deux fragments pour la même info. Choisis le bon sujet. [cite: 2026-02-10]
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Boran aime le chocolat au lait", "path": "Archives/Utilisateur/Gouts/Alimentaire"}} ] }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": tree_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        data = json.loads(chat_completion.choices[0].message.content)
        fragments = data.get("fragments", [])[:1] # Limite stricte à 1 fragment pour éviter le mélange [cite: 2026-02-10]
        results = []

        for item in fragments:
            content, path = item.get("content"), item.get("path")
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
