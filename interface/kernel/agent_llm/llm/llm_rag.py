import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v6.7 : Identité Suprême & Distinction Nominale.
    Gère Boran (Prénom), Sezer (Nom) et les entités tierces (Bedran, Zilan).
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Mots-Clés Étendus) ---
        keywords = ["ans", "âge", "aime", "adore", "préfère", "frère", "sœur", "famille", "chocolat", "boran", "sezer", "bedran", "zilan"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Précision Nominale) ---
        tree_prompt = f"""
        Tu es le cartographe de DELTA. Donnée : "{prompt}"
        
        RÈGLES D'IDENTITÉ STRICTES :
        1. UTILISATEUR : Ton créateur s'appelle Boran SEZER. 
           - Prénom -> Archives/Utilisateur/Identite/Prenom
           - Nom -> Archives/Utilisateur/Identite/Nom
           - Ses goûts -> Archives/Utilisateur/Gouts/Alimentaire
        
        2. TIERS : Tu DOIS extraire le prénom (ex: Bedran, Zilan) pour le chemin. [cite: 2026-02-10]
           - Archives/Social/Famille/[Prenom]/Age
           - Archives/Social/Famille/[Prenom]/Gouts
        
        3. VÉRITÉ : Ne confonds jamais les goûts de Boran avec ceux de sa famille. [cite: 2026-02-10]
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Sujet exact + info", "path": "Archives/..."}} ] }}
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

        # --- SAUVEGARDE ET UPSERT ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            embedding = generate_embedding(content)
            
            # L'Upsert se base sur le path unique [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
