import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v7.6 : Noyau Jarvis Final.
    Validation par Monsieur Sezer (Boran) le 10/02/2026.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : DÉTECTION DE FAITS ---
        keywords = ["ans", "âge", "aime", "chocolat", "frère", "sœur", "bedran", "zilan", "boran", "pardon"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : ARCHIVAGE NOMINAL ---
        tree_prompt = f"""
        Donnée utilisateur : "{prompt}"
        RÈGLE : Utilise TOUJOURS le prénom (Boran, Bedran, Zilan) dans le contenu.
        
        STRUCTURE :
        - Moi/Je -> Archives/Utilisateur/Identite/Age ou /Gouts/Alimentaire
        - Bedran -> Archives/Social/Famille/Bedran/Age ou /Gouts
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Boran [Action] [Objet]", "path": "Archives/..."}} ] }}
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
            
            # Sauvegarde forcée sans filtre restrictif
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
