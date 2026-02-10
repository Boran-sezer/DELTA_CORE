import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v5.1 : Archivage Arborescent avec Contexte Explicite.
    Force l'inclusion du sujet dans chaque fragment pour garantir la réussite du RAG.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Identification des faits) ---
        filter_prompt = f"Analyse : '{prompt}'. Si c'est une info sur la vie, une personne ou un fait, réponds 'MEMO'. Sinon 'IGNORE'."
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant"
        )
        
        if "IGNORE" in check_task.choices[0].message.content.upper():
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Fusion Contexte + Branche) ---
        tree_prompt = f"""
        Tu es le cartographe de l'Arbre de Connaissance de Monsieur Sezer.
        Donnée : "{prompt}"
        
        TON RÔLE : 
        1. Identifie le sujet (ex: Bedran).
        2. Crée une branche précise (ex: Archives/Social/Famille/Frere/Bedran/Alimentation).
        
        RÈGLE D'OR D'INTELLIGENCE :
        - Chaque 'content' doit être AUTONOME. [cite: 2026-02-10]
        - RE-INJECTE TOUJOURS le sujet dans la phrase. [cite: 2026-02-10]
        - INTERDICTION de phrases sans sujet comme "Aime la pizza".
        - EXEMPLE : "Bedran aime la pizza et déteste les oignons."
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Sujet + Verbe + Information", "path": "Archives/..."}} ] }}
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
            
            # Protection contre les fragments inutiles
            if len(content.split()) < 4: 
                continue
                
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée (pollution)."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
