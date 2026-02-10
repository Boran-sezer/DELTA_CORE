import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v7.2 : Logique Comparative & Archivage Chirurgical.
    Version finale validée par Monsieur Sezer le 10/02/2026.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Capture de Faits) ---
        keywords = ["ans", "âge", "aime", "chocolat", "crêpe", "plat", "frère", "sœur", "bedran", "zilan", "boran", "sezer"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Vérité Absolue) ---
        # On force l'IA à nommer Boran ou Bedran dans le texte pour éviter les "Lui" [cite: 2026-02-10]
        tree_prompt = f"""
        Tu es le cerveau de DELTA. Donnée : "{prompt}"
        
        RÈGLES D'ARCHIVAGE :
        1. IDENTITÉ : "Je/Moi" = Boran (Monsieur Sezer). "Il/Lui/Frère" = Bedran. "Sœur" = Zilan.
        2. CONTENU : Interdiction d'utiliser des pronoms flous. Remplace "il aime" par "Bedran aime". [cite: 2026-02-10]
        3. CHEMINS : 
           - Boran -> Archives/Utilisateur/Identite/Age ou /Gouts/Alimentaire
           - Bedran -> Archives/Social/Famille/Bedran/Age ou /Gouts
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Sujet (Nom) + Action + Objet", "path": "Archives/..."}} ] }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": tree_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        data = json.loads(chat_completion.choices[0].message.content)
        fragments = data.get("fragments", [])[:2]
        results = []

        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # Validation du chemin (Doit commencer par Archives/) [cite: 2026-02-10]
            if not path.startswith("Archives/"):
                continue
                
            embedding = generate_embedding(content)
            
            # Sauvegarde avec Upsert (écrase l'ancienne valeur sur le même chemin) [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
