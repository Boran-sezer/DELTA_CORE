import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v7.3 : Master Logic.
    Sépare strictement Boran et Bedran pour éviter les contradictions orales.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Capture de Faits) ---
        keywords = ["ans", "âge", "aime", "chocolat", "frère", "bedran", "zilan", "boran", "sezer", "pardon"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Logique de Sujet) ---
        tree_prompt = f"""
        Donnée : "{prompt}"
        
        RÈGLES D'IDENTITÉ :
        - SI la phrase contient "il", "lui" ou "Bedran" -> Sujet = Bedran. [cite: 2026-02-10]
        - SI la phrase contient "Je", "Moi" ou "Mon" -> Sujet = Boran. [cite: 2026-02-10]
        
        CONTENU JSON : Le contenu DOIT commencer par le nom du sujet pour lever toute ambiguïté.
        Exemple : "Bedran aime le chocolat noir" ou "Boran aime le chocolat au lait". [cite: 2026-02-10]
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
            if not path.startswith("Archives/"): continue
                
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
        
