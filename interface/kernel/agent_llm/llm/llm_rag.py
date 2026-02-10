import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v5.7 : Archivage Forcé Monsieur Sezer.
    Identifie, classifie et écrase les anciennes données (Upsert).
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Version Armure Monsieur Sezer) ---
        # Zéro tolérance à l'hésitation pour vos informations personnelles [cite: 2026-02-10]
        filter_prompt = f"""
        Tu es le garde-barrière de DELTA. Phrase : "{prompt}"
        
        RÈGLE ABSOLUE :
        - Si la phrase contient un chiffre (âge), une préférence (chocolat), un nom ou un fait sur la vie de Monsieur Sezer, réponds EXCLUSIVEMENT 'MEMO'. [cite: 2026-02-10]
        - Ne réfléchis pas à l'utilité. Si c'est un fait sur l'utilisateur : 'MEMO'. [cite: 2026-02-10]
        - Uniquement si c'est une formule de politesse vide (Salut, Ça va), réponds 'IGNORE'.
        
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
        # Force l'utilisation de chemins profonds pour l'Upsert
        tree_prompt = f"""
        Tu es le cartographe de DELTA. Donnée : "{prompt}"
        
        RÈGLES D'AUTOMATISATION :
        1. Sujet : Utilise "Monsieur Sezer" par défaut. [cite: 2026-02-08]
        2. INTERDICTION d'utiliser des chemins courts (ex: Archives/Utilisateur/Identite).
        3. STRUCTURES OBLIGATOIRES (pour permettre l'Upsert) :
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
            
            # Sécurité anti-résidus : on refuse les chemins trop courts
            if len(path.split('/')) < 4:
                continue
                
            embedding = generate_embedding(content)
            
            # save_to_memory doit utiliser .upsert(data, on_conflict='path') [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée (chemin imprécis)."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
