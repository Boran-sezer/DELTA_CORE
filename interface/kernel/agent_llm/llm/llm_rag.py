import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v6.2 : Isolation des Profils & Upsert Sélectif.
    Empêche l'écrasement des données de Monsieur Sezer par des tiers.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Agressivité Totale) ---
        filter_prompt = f"""
        Phrase : "{prompt}"
        Si la phrase contient une info sur Monsieur Sezer, Bedran, la famille, 
        un âge ou un goût, réponds 'MEMO'. Sinon 'IGNORE'.
        """
        
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        
        if "MEMO" not in check_task.choices[0].message.content.upper():
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Isolation Monsieur Sezer vs Autres) ---
        # On force la création de dossiers séparés [cite: 2026-02-10]
        tree_prompt = f"""
        Tu es le cartographe. Donnée : "{prompt}"
        
        RÈGLES DE CHEMINS (Upsert Safe) :
        1. MONSIEUR SEZER : Utilise UNIQUEMENT :
           - Archives/Utilisateur/Identite/Age
           - Archives/Utilisateur/Gouts/Alimentaire
        
        2. TIERS (Ex: Bedran) : Ne touche JAMAIS aux chemins 'Utilisateur'. Crée :
           - Archives/Social/Famille/[Nom]/Age
           - Archives/Social/Famille/[Nom]/Relation
        
        RÉPONDS EN JSON :
        {{ "fragments": [ {{"content": "Phrase complète", "path": "Le chemin correct"}} ] }}
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

        # --- SAUVEGARDE DIRECTE ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            embedding = generate_embedding(content)
            
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
