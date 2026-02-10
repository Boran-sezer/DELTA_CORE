import streamlit as st
import json
import re
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système de tri Multi-Agent DELTA.
    Phase 1 : Filtrage des questions.
    Phase 2 : Fragmentation atomique par bloc de sens.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Évite d'enregistrer les questions) ---
        # Utilisation d'un modèle rapide (8b) pour l'analyse de flux.
        filter_prompt = f"""
        Analyse la phrase : "{prompt}"
        Est-ce une information à mémoriser (affirmation) ou une question/salutation ?
        RÉPONDS UNIQUEMENT PAR 'MEMO' OU 'IGNORE'.
        """
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant"
        )
        
        if "IGNORE" in check_task.choices[0].message.content.upper():
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : L'ARCHIVISTE (Fragmentation & Tri) ---
        # Utilisation du modèle 70b pour la structure JSON complexe. [cite: 2026-02-10]
        fragmentation_prompt = f"""
        Tu es l'archiviste de Monsieur Sezer. Décompose cette phrase en fragments UTILES : "{prompt}"
        
        RÈGLES CRUCIALES :
        1. Garde le sujet et l'action ensemble (ex: "Jules a 17 ans"). [cite: 2026-02-10]
        2. Crée des chemins précis : 'Social/Amis/[Nom]', 'Social/Famille/[Lien]', 'Utilisateur/Identite'. [cite: 2026-02-10]
        
        FORMAT JSON STRICT :
        {{
          "fragments": [
            {{"content": "...", "path": "..."}}
          ]
        }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": fragmentation_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        data = json.loads(chat_completion.choices[0].message.content)
        fragments = data.get("fragments", [])
        results = []

        # --- SAUVEGARDE ATOMIQUE ---
        for item in fragments:
            content = item.get("content")
            path = item.get("path")
            
            embedding = generate_embedding(content)
            success = save_to_memory(content, embedding, path)
            
            if success:
                results.append(path)

        return f"Multi-archivage réussi : {', '.join(set(results))}"

    except Exception as e:
        return f"Erreur Système : {str(e)}"
