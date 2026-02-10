import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v6.5 : Cartographie Dynamique et Extraction d'Entités.
    Sépare Monsieur Sezer des tiers de manière automatique.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Détection de Mots-Clés) ---
        # On force le passage si un mot lié à l'identité ou aux goûts est présent [cite: 2026-02-10]
        keywords = ["ans", "âge", "aime", "adore", "préfère", "frère", "ami", "famille", "chocolat", "sezer"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE DYNAMIQUE ---
        # Ce prompt force l'IA à trouver le sujet de la phrase pour choisir le bon chemin [cite: 2026-02-10]
        tree_prompt = f"""
        Tu es le cartographe universel de DELTA. Donnée : "{prompt}"
        
        RÈGLES D'ORIENTATION :
        1. SUJET = MONSIEUR SEZER : (Si "Je", "Moi", "Mon âge", "Mes goûts")
           - Age -> Archives/Utilisateur/Identite/Age
           - Gouts -> Archives/Utilisateur/Gouts/Alimentaire
        
        2. SUJET = TIERS : (Si un prénom est cité ou "Mon frère", "Mon ami")
           - EXTRAIS le prénom (ex: Bedran, Lucas).
           - Age -> Archives/Social/Famille/[Nom]/Age
           - Gouts -> Archives/Social/Famille/[Nom]/Gouts
        
        CONSIGNE : Ne mélange jamais les chemins 'Utilisateur' et 'Social'. [cite: 2026-02-10]
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Sujet + info précise", "path": "Archives/..."}} ] }}
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
            
            # On génère l'embedding pour la recherche vectorielle future
            embedding = generate_embedding(content)
            
            # L'Upsert se base sur le 'path' unique pour écraser ou créer [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
