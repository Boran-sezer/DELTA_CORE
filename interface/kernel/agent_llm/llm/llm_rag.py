import streamlit as st
import json
import re
import time
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v12.0 : Singularity.
    Correction du bug de polarité sémantique et optimisation Lux AI.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        start_time = time.time()
        
        # --- FILTRE DE DÉTECTION (Sensibilité Alpha) ---
        patterns = r"(ans|âge|aime|adore|chocolat|crêpe|frère|sœur|bedran|zilan|boran|pardon|non|pas|trompé|préfère)"
        if not re.search(patterns, prompt.lower()):
            return "Système en veille."

        # --- LOGIQUE DE RÉÉCRITURE POSITIVE (Anti-Bug) ---
        singularity_prompt = f"""
        SYSTÈME : Noyau Singularity v12. Donnée : "{prompt}"
        
        RÈGLES CRITIQUES :
        1. POLARITÉ : Si l'utilisateur dit "non je me suis trompé, je préfère X", l'archive doit être AFFIRMATIVE ("Boran aime X"). Ne jamais écrire "préfère contre".
        2. SUJET : Boran (Utilisateur) vs Bedran/Zilan (Social).
        3. QUALITÉ : Transforme l'input en fait historique définitif.
        
        RÉPONDS EN JSON :
        {{ "fragments": [ {{"content": "Boran apprécie le chocolat au lait", "path": "Archives/Utilisateur/Gouts/Alimentaire"}} ] }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": "Expert en sémantique positive."},
                      {"role": "user", "content": singularity_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        data = json.loads(chat_completion.choices[0].message.content)
        fragments = data.get("fragments", [])[:1]

        results = []
        for item in fragments:
            content, path = item.get("content"), item.get("path").strip().replace(" ", "")
            if not path.startswith("Archives/"): path = "Archives/" + path
            
            # Vectorisation et Upsert
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        exec_duration = round(time.time() - start_time, 2)
        return f"🛡️ Singularity v12 activé ({exec_duration}s) : {', '.join(results)}"

    except Exception as e:
        return f"⚠️ Erreur Noyau : {str(e)}"
