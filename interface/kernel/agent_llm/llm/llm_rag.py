import streamlit as st
import json
import re
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système de tri Multi-Agent DELTA v3.0 (Cohésion Maximale).
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Ajusté pour éviter la pollution) ---
        filter_prompt = f"""
        Analyse la phrase : "{prompt}"
        Est-ce une information factuelle à retenir ou une simple question/salutation ?
        RÉPONDS UNIQUEMENT PAR 'MEMO' OU 'IGNORE'.
        """
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant"
        )
        
        if "IGNORE" in check_task.choices[0].message.content.upper():
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : L'ARCHIVISTE (Version Anti-Fragmentation) ---
        fragmentation_prompt = f"""
        Tu es l'archiviste de Monsieur Sezer. Analyse : "{prompt}"
        
        CONSIGNES DE SÉCURITÉ :
        1. NE DÉCOUPE PAS les faits. Une ligne doit contenir Sujet + Lien + Info (ex: "Bedran a 26 ans").
        2. INTERDICTION de créer des fragments vides ou sans contexte (ex: "quelle age").
        3. Si la phrase contient plusieurs infos, crée un fragment complet pour chacune.
        
        STRUCTURE :
        - 'Social/Amis/[Nom]'
        - 'Social/Famille/[Lien]'
        - 'Utilisateur/Identite'
        
        RÉPONDS EN JSON :
        {{ "fragments": [ {{"content": "...", "path": "..."}} ] }}
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

        # --- SAUVEGARDE ET NETTOYAGE ---
        for item in fragments:
            content = item.get("content")
            path = item.get("path")
            
            # Sécurité supplémentaire : On ignore les fragments trop courts (pollution)
            if len(content.split()) < 3:
                continue
                
            embedding = generate_embedding(content)
            success = save_to_memory(content, embedding, path)
            
            if success:
                results.append(path)

        if not results:
            return "Aucune information pertinente à archiver."

        return f"Multi-archivage réussi : {', '.join(set(results))}"

    except Exception as e:
        return f"Erreur Système : {str(e)}"
