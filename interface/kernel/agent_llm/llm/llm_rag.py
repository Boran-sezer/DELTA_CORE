import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v5.4 : Archivage Prioritaire Monsieur Sezer.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Priorité Créateur & Corrections) ---
        # On force le MEMO pour tout ce qui touche à Monsieur Sezer [cite: 2026-02-08]
        filter_prompt = f"""
        Analyse la phrase suivante de l'utilisateur : "{prompt}"
        
        INSTRUCTIONS :
        1. Si la phrase parle de Monsieur Sezer (Boran), de sa famille (Bedran), de son âge ou de ses goûts, réponds 'MEMO'. [cite: 2026-02-10]
        2. Si c'est une correction d'une information passée, réponds 'MEMO'. [cite: 2026-02-10]
        3. Si c'est juste un bonjour ou une phrase sans aucun fait, réponds 'IGNORE'.
        
        RÉPONSE UNIQUE : 'MEMO' ou 'IGNORE'.
        """
        
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0 # Zéro température pour éviter les hésitations du filtre
        )
        
        decision = check_task.choices[0].message.content.upper()
        
        if "IGNORE" in decision and "MEMO" not in decision:
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Intelligence de Branche) ---
        tree_prompt = f"""
        Tu es le cartographe de l'Arbre de Connaissance de Monsieur Sezer.
        Donnée à classer : "{prompt}"
        
        RÈGLES :
        - Crée un chemin précis (ex: Archives/Utilisateur/Identite ou Archives/Social/Famille/Bedran/Age).
        - Ré-écris le contenu pour qu'il soit complet (ex: "Monsieur Sezer Boran a 17 ans"). [cite: 2026-02-10]
        
        RÉPONDS EN JSON :
        {{ "fragments": [ {{"content": "Phrase complète avec sujet", "path": "Chemin/Vers/Branche"}} ] }}
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

        # --- SAUVEGARDE (Upsert activé par le SQL UNIQUE) ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            if len(content.split()) < 3: 
                continue
                
            embedding = generate_embedding(content)
            # Utilise l'upsert basé sur la contrainte UNIQUE (path) [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
