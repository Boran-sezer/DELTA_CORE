import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v5.6 : Élimination des résidus et automatisation totale.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Priorité Monsieur Sezer) ---
        filter_prompt = f"""
        Analyse : "{prompt}"
        Si c'est un fait sur Monsieur Sezer, sa famille, ou une correction, réponds 'MEMO'. 
        Sinon réponds 'IGNORE'.
        """
        
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        
        if "MEMO" not in check_task.choices[0].message.content.upper():
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Zéro Résidu) ---
        tree_prompt = f"""
        Tu es le cartographe de DELTA. Donnée : "{prompt}"
        
        RÈGLES D'AUTOMATISATION :
        1. INTERDICTION d'utiliser des chemins courts comme 'Archives/Utilisateur/Identite'.
        2. Tu dois TOUJOURS aller jusqu'au bout de l'arborescence pour que l'Upsert fonctionne. [cite: 2026-02-10]
        3. CHEMINS OBLIGATOIRES :
           - Âge -> Archives/Utilisateur/Identite/Age
           - Localisation -> Archives/Utilisateur/Identite/Localisation
           - Famille -> Archives/Utilisateur/Famille/Composition
           - Gouts -> Archives/Utilisateur/Gouts/Alimentaire
        
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

        # --- SAUVEGARDE (L'Upsert remplace automatiquement l'info au même chemin) ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # Sécurité : On refuse les chemins trop courts qui créent des doublons
            if len(path.split('/')) < 4:
                continue

            embedding = generate_embedding(content)
            # save_to_memory utilise .upsert(data, on_conflict='path') [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée (chemin imprécis)."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
