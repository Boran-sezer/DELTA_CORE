import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v5.8 : Chemins Fixes et Écrasement Obligatoire.
    Conçu pour une automatisation totale sans intervention sur Supabase.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Priorité Absolue Monsieur Sezer) ---
        filter_prompt = f"""
        Tu es le garde-barrière. Phrase : "{prompt}"
        Si la phrase contient un fait, une préférence ou un chiffre sur Monsieur Sezer, réponds 'MEMO'. 
        Sinon (salutations seules, phrases vides), réponds 'IGNORE'.
        RÉPONSE : 'MEMO' ou 'IGNORE'.
        """
        
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        
        if "MEMO" not in check_task.choices[0].message.content.upper():
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Discipline des Tiroirs) ---
        # On interdit la création de sous-branches pour garantir l'Upsert [cite: 2026-02-10]
        tree_prompt = f"""
        Tu es le cartographe de DELTA. Donnée : "{prompt}"
        
        RÈGLES DE FER :
        1. Utilise EXCLUSIVEMENT ces chemins exacts pour permettre l'écrasement (Upsert) :
           - Archives/Utilisateur/Identite/Age
           - Archives/Utilisateur/Gouts/Alimentaire
           - Archives/Utilisateur/Famille/Composition
        
        2. INTERDICTION de créer des sous-chemins (ex: pas de '/Non_Preferes'). 
           Si l'info change, on écrase le contenu du chemin existant. [cite: 2026-02-10]
        
        3. CONTENU : Toujours une phrase complète incluant "Monsieur Sezer".
        
        RÉPONDS EN JSON :
        {{ "fragments": [ {{"content": "Monsieur Sezer + info", "path": "Archives/..."}} ] }}
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

        # --- SAUVEGARDE (L'Upsert écrase la ligne si le path est identique) ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # Sécurité : On refuse les contenus trop pauvres (ex: juste un chiffre)
            if len(content.split()) < 3:
                continue
                
            embedding = generate_embedding(content)
            
            # Rappel : save_to_memory doit utiliser .upsert(data, on_conflict='path') [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
