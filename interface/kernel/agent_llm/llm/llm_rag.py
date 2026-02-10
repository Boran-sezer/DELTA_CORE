import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v5.9 : Archivage Systématique Monsieur Sezer.
    Écrase les données même en cas de répétition pour garantir la mémorisation.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Agressivité Totale) ---
        filter_prompt = f"""
        Tu es le garde-barrière. Analyse : "{prompt}"
        RÈGLE : Si la phrase parle de Monsieur Sezer (goûts, âge, identité), réponds 'MEMO'.
        Même si c'est une répétition, réponds 'MEMO'. [cite: 2026-02-10]
        Sinon réponds 'IGNORE'.
        """
        
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        
        if "MEMO" not in check_task.choices[0].message.content.upper():
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Tiroirs Verrouillés) ---
        tree_prompt = f"""
        Tu es le cartographe. Donnée : "{prompt}"
        
        INTERDICTION de créer des nouveaux chemins. Utilise UNIQUEMENT :
        - Archives/Utilisateur/Identite/Age
        - Archives/Utilisateur/Gouts/Alimentaire
        - Archives/Utilisateur/Famille/Composition
        
        CONSIGNE : Reformule pour que le contenu soit une affirmation claire. [cite: 2026-02-10]
        
        RÉPONDS EN JSON :
        {{ "fragments": [ {{"content": "Monsieur Sezer aime le chocolat au lait", "path": "Archives/Utilisateur/Gouts/Alimentaire"}} ] }}
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

        # --- SAUVEGARDE SANS FILTRE DE LONGUEUR ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # On retire la barrière des 3 mots pour laisser passer les confirmations courtes [cite: 2026-02-10]
            embedding = generate_embedding(content)
            
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
