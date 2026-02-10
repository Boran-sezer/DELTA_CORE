import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v5.6 : Automatisation Totale Monsieur Sezer.
    Identifie, classifie et écrase les anciennes données (Upsert).
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Priorité Absolue Créateur) ---
        # On force le MEMO pour tout ce qui touche à Monsieur Sezer [cite: 2026-02-10]
        filter_prompt = f"""
        Analyse la phrase : "{prompt}"
        
        CONSIGNE :
        Si la phrase contient une info sur Monsieur Sezer (Boran), sa famille, son âge, 
        ses goûts (ex: chocolat), ou une correction de fait, réponds TOUJOURS 'MEMO'. 
        Sinon réponds 'IGNORE'.
        
        RÉPONSE : 'MEMO' ou 'IGNORE'.
        """
        
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        
        decision = check_task.choices[0].message.content.upper()
        
        if "MEMO" not in decision:
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Zéro Résidu / Chemins Fixes) ---
        # Force l'utilisation de chemins profonds pour éviter les doublons
        tree_prompt = f"""
        Tu es le cartographe de DELTA. Donnée à traiter : "{prompt}"
        
        RÈGLES DE CLASSIFICATION :
        1. Sujet : Utilise "Monsieur Sezer" par défaut.
        2. Chemins : INTERDICTION d'utiliser des chemins courts (ex: Archives/Utilisateur/Identite). [cite: 2026-02-10]
        3. STRUCTURES OBLIGATOIRES (pour l'Upsert) :
           - Âge -> Archives/Utilisateur/Identite/Age
           - Gouts -> Archives/Utilisateur/Gouts/Alimentaire
           - Famille -> Archives/Utilisateur/Famille/Composition
        
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

        # --- SAUVEGARDE & UPSERT ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # Sécurité : On refuse les chemins trop vagues [cite: 2026-02-10]
            if len(path.split('/')) < 4:
                continue
                
            embedding = generate_embedding(content)
            
            # save_to_memory doit utiliser .upsert(data, on_conflict='path') [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée (chemin imprécis)."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
