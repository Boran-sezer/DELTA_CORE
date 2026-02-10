import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v6.1 : Forçage par Mots-Clés.
    Supprime toute hésitation du filtre pour Monsieur Sezer.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Zéro Intelligence, Pur Automatisme) ---
        # On force le MEMO si un mot clé de votre vie apparaît [cite: 2026-02-10]
        filter_prompt = f"""
        Phrase à analyser : "{prompt}"
        
        INSTRUCTION : 
        Si la phrase contient 'ans', 'âge', 'aime', 'adore', 'préfère', 'frère', 'famille' ou 'Sezer', 
        tu réponds obligatoirement 'MEMO'. [cite: 2026-02-10]
        Peu importe si l'info est déjà connue.
        Sinon, réponds 'IGNORE'.
        
        RÉPONSE UNIQUE : 'MEMO' ou 'IGNORE'.
        """
        
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        
        decision = check_task.choices[0].message.content.upper()
        
        if "MEMO" not in decision:
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Structure Immuable) ---
        tree_prompt = f"""
        Tu es le cartographe. Donnée : "{prompt}"
        
        Utilise EXCLUSIVEMENT ces chemins :
        - Archives/Utilisateur/Identite/Age
        - Archives/Utilisateur/Gouts/Alimentaire
        - Archives/Utilisateur/Famille/Composition
        
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

        # --- SAUVEGARDE DIRECTE (Sans aucune condition de longueur) ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            embedding = generate_embedding(content)
            
            # Rappel : save_to_memory doit impérativement utiliser .upsert() [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
