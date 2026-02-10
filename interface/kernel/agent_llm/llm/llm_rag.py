import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v5.0 : Archivage en Arbre Récursif Infini.
    Génère des branches et sous-branches dynamiques selon le contexte.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Identification des faits) ---
        filter_prompt = f"Analyse : '{prompt}'. Si c'est une info sur la vie, une personne ou un fait, réponds 'MEMO'. Sinon 'IGNORE'."
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant"
        )
        
        if "IGNORE" in check_task.choices[0].message.content.upper():
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Branches infinies) ---
        # Utilisation du 70b pour une logique de ramification parfaite. [cite: 2026-02-10]
        tree_prompt = f"""
        Tu es le cartographe de l'Arbre de Connaissance de Monsieur Sezer.
        Donnée : "{prompt}"
        
        TON RÔLE : 
        1. Identifie le sujet principal.
        2. Crée une branche logique (ex: Archives/Social/Famille/Frere/Bedran).
        3. Si l'info est précise, crée une sous-sous-branche (ex: .../Bedran/Age).
        
        RÈGLES D'OR :
        - Profondeur infinie autorisée selon le besoin. [cite: 2026-02-10]
        - Une branche = Une fiche complète (Sujet + Action + Info). [cite: 2026-02-10]
        - Ignore les pollutions (mots isolés, chiffres seuls).
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Description riche du nœud", "path": "Archives/Branche/SousBranche/..."}} ] }}
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

        # --- SAUVEGARDE ET VALIDATION ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # Protection contre les fragments trop courts (pollution type ID 67)
            if len(content.split()) < 3: 
                continue
                
            embedding = generate_embedding(content)
            # Note : Assurez-vous que save_to_memory gère l'UPSERT sur le champ 'path'
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée (pollution)."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
