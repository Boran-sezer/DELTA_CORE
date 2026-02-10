import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v5.3 : Archivage Arborescent avec Gestion des Corrections.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Acceptation des corrections) ---
        # Correction : Ajout explicite des corrections d'âge et de faits [cite: 2026-02-10]
        filter_prompt = (
            f"Analyse : '{prompt}'. Si c'est une info nouvelle, une correction d'âge, "
            "un nom ou un fait, réponds 'MEMO'. Sinon 'IGNORE'."
        )
        
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant"
        )
        
        if "IGNORE" in check_task.choices[0].message.content.upper():
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Intelligence de mise à jour) ---
        tree_prompt = f"""
        Tu es le cartographe de l'Arbre de Connaissance de Monsieur Sezer.
        Donnée : "{prompt}"
        
        TON RÔLE : 
        1. Identifie le sujet.
        2. Utilise EXACTEMENT le même chemin (path) pour une correction (ex: .../Bedran/Age).
        
        RÈGLE D'OR :
        - Chaque 'content' doit être AUTONOME avec le sujet inclus. [cite: 2026-02-10]
        - RE-INJECTE TOUJOURS le sujet dans la phrase (ex: "Bedran a 27 ans"). [cite: 2026-02-10]
        
        RÉPONDS EN JSON :
        {{ "fragments": [ {{"content": "Sujet + Info", "path": "Archives/..."}} ] }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": tree_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        data = json.loads(chat_completion.choices[0].message.content)
        fragments = data.get("fragments", [])
        results = []

        # --- SAUVEGARDE ET VALIDATION ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            if len(content.split()) < 4: 
                continue
                
            embedding = generate_embedding(content)
            # Rappel : save_to_memory doit utiliser 'upsert' sur le champ 'path' [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
