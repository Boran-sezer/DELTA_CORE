import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v6.8 : Limitation de Flux et Précision Chirurgicale.
    Empêche la prolifération de tiroirs vides et les doublons.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Mots-Clés de Vie) ---
        keywords = ["ans", "âge", "aime", "adore", "préfère", "frère", "sœur", "famille", "chocolat", "boran", "sezer", "zilan"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Sélectif) ---
        tree_prompt = f"""
        Tu es le cartographe de DELTA. Donnée : "{prompt}"
        
        RÈGLES DE RANGEMENT STRICTES :
        1. INTERDICTION : Ne crée JAMAIS de chemin parent comme 'Archives/Utilisateur/Identite'.
        2. OBLIGATION : Utilise uniquement des sous-tiroirs finaux : /Age, /Prenom, /Nom, /Alimentaire. [cite: 2026-02-10]
        3. ÉCONOMIE : Ne génère qu'UN SEUL fragment par information. Si l'utilisateur donne son âge, n'envoie que le tiroir /Age.
        4. ISOLATION : Si l'utilisateur ne parle pas de Bedran ou Zilan, ne les mentionne pas dans le JSON. [cite: 2026-02-10]
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Sujet + fait précis", "path": "Archives/..."}} ] }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": tree_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        data = json.loads(chat_completion.choices[0].message.content)
        fragments = data.get("fragments", [])[:2] # Force la limite à 2 fragments maximum [cite: 2026-02-10]
        results = []

        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # Sécurité : On ignore les chemins trop courts ou racine [cite: 2026-02-10]
            if path.count('/') < 3:
                continue
                
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée (trop générique)."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
