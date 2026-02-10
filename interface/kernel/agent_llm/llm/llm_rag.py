import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v5.5 : Archivage par Écrasement (Upsert) & Chemins Fixes.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Priorité Absolue Créateur) ---
        filter_prompt = f"""
        Analyse la phrase : "{prompt}"
        Si elle contient une info sur Monsieur Sezer, sa famille, son âge ou ses goûts, réponds 'MEMO'. 
        Si c'est une correction de chiffre ou de fait, réponds 'MEMO'. [cite: 2026-02-10]
        Sinon réponds 'IGNORE'.
        """
        
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        
        if "MEMO" not in check_task.choices[0].message.content.upper():
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Standardisation des Chemins) ---
        tree_prompt = f"""
        Tu es le cartographe de DELTA. Donnée : "{prompt}"
        
        CONSIGNES DE RIGUEUR :
        1. IDENTITÉ : Ne cite JAMAIS "Bedran" sauf si l'utilisateur l'a nommé. Sinon, utilise "Monsieur Sezer". [cite: 2026-02-10]
        2. CHEMINS FIXES : Pour permettre l'Upsert, utilise TOUJOURS ces structures :
           - Archives/Utilisateur/Identite/Age
           - Archives/Utilisateur/Gouts/Alimentaire
           - Archives/Utilisateur/Famille/Composition (pour le nombre de frères/sœurs)
           - Archives/Social/Famille/Bedran/[Sujet] (uniquement si Bedran est cité)
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Monsieur Sezer + info complète", "path": "Archives/..."}} ] }}
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

        # --- SAUVEGARDE (L'Upsert écrase l'ancienne ligne avec le même path) ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            if len(content.split()) < 3: continue
                
            embedding = generate_embedding(content)
            # Appel à save_to_memory qui doit utiliser upsert(data, on_conflict='path') [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
