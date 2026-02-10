import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v6.3 : Archivage par Mots-Clés Prioritaires.
    Garantit que même les corrections "au vol" sont capturées.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Détection de Mots-Clés) ---
        # On force le MEMO si un mot critique est présent [cite: 2026-02-10]
        keywords = ["ans", "âge", "aime", "adore", "préfère", "frère", "famille", "chocolat", "sezer", "bedran"]
        lower_prompt = prompt.lower()
        
        is_memo = any(word in lower_prompt for word in keywords)
        
        if not is_memo:
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Isolation des Tiroirs) ---
        # On impose la séparation stricte Monsieur Sezer / Bedran [cite: 2026-02-10]
        tree_prompt = f"""
        Tu es le cartographe. Donnée : "{prompt}"
        
        RÈGLES DE CHEMINS (Upsert Force) :
        1. MONSIEUR SEZER (Toi) : 
           - Age -> Archives/Utilisateur/Identite/Age
           - Gouts -> Archives/Utilisateur/Gouts/Alimentaire
        
        2. BEDRAN / AUTRES :
           - Archives/Social/Famille/Bedran/Age
           - Archives/Social/Famille/Bedran/Relation
        
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

        # --- SAUVEGARDE DIRECTE ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            embedding = generate_embedding(content)
            
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
