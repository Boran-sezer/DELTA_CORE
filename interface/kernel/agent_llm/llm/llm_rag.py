import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v6.6 : Vérité Absolue Monsieur Sezer.
    Verrouille l'identité et empêche les hallucinations entre profils.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Mots-Clés de Vie) ---
        keywords = ["ans", "âge", "aime", "adore", "préfère", "frère", "famille", "chocolat", "sezer", "bedran"]
        if not any(word in prompt.lower() for word in keywords):
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Logique de Vérité) ---
        # On force l'IA à être factuelle et à ne pas mélanger les goûts [cite: 2026-02-10]
        tree_prompt = f"""
        Tu es le cartographe de DELTA. Donnée : "{prompt}"
        
        RÈGLES D'ISOLATION ET DE VÉRITÉ :
        1. "JE/MOI" = Monsieur Sezer uniquement. 
           - Age -> Archives/Utilisateur/Identite/Age
           - Gouts -> Archives/Utilisateur/Gouts/Alimentaire
        
        2. "IL/BEDRAN" = Social/Famille/Bedran.
           - Age -> Archives/Social/Famille/Bedran/Age
           - Gouts -> Archives/Social/Famille/Bedran/Gouts
        
        3. INTERDICTION : Si Bedran aime le chocolat noir, n'écris JAMAIS que Monsieur Sezer l'aime aussi. 
           Chaque fait doit être strictement rattaché à son sujet. [cite: 2026-02-10]
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "Sujet exact + info factuelle", "path": "Archives/..."}} ] }}
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

        # --- SAUVEGARDE & UPSERT SANS FILTRE DE LONGUEUR ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            embedding = generate_embedding(content)
            
            # L'Upsert se base sur le 'path' pour écraser l'ancienne donnée [cite: 2026-02-10]
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
