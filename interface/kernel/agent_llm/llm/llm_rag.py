import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v6.9 : Équilibre Précision/Acceptation.
    Ajustement des filtres pour valider les dossiers d'identité et de goûts.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Mots-Clés) ---
        keywords = ["ans", "âge", "aime", "adore", "chocolat", "boran", "sezer", "bedran", "zilan"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Structure Rectifiée) ---
        tree_prompt = f"""
        Tu es le cartographe de DELTA. Donnée : "{prompt}"
        
        RÈGLES DE CHEMINS :
        - Monsieur Sezer -> Archives/Utilisateur/Identite/Age OU Archives/Utilisateur/Gouts/Alimentaire
        - Tiers -> Archives/Social/Famille/[Prenom]/Info
        
        CONSIGNE : Sois précis. N'utilise pas de dossiers racines seuls.
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Fait précis", "path": "Archives/..."}} ] }}
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
            
            # Ajustement : On accepte à partir de 2 slashs (ex: Archives/Utilisateur/Age) [cite: 2026-02-10]
            if path.count('/') < 2:
                continue
                
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée (chemin invalide)."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
