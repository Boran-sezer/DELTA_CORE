import streamlit as st
import json
import re
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système de fragmentation atomique de DELTA.
    Extraction JSON sécurisée par Regex.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        fragmentation_prompt = f"""
        Tu es le processeur de DELTA. Décompose cette phrase en fragments atomiques : "{prompt}"
        
        RÈGLES :
        - 'Utilisateur/Identite' : Infos sur Sezer Boran.
        - 'Social/Amis' : Infos sur des tiers (Jules, etc.).
        
        RÉPONDS UNIQUEMENT AU FORMAT JSON :
        {{
          "fragments": [
            {{"content": "...", "path": "..."}}
          ]
        }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": fragmentation_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0, # Plus de stabilité
        )
        
        raw_response = chat_completion.choices[0].message.content

        # --- SÉCURITÉ JSON : Nettoyage par Expression Régulière ---
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            # Fallback si le JSON est mal formé
            return "⚠️ Erreur : Format de réponse IA invalide."

        fragments = data.get("fragments", [])
        results = []

        for item in fragments:
            content = item.get("content")
            path = item.get("path")
            
            embedding = generate_embedding(content)
            success = save_to_memory(content, embedding, path)
            
            if success:
                results.append(f"{path}")

        return f"✅ Multi-archivage : {', '.join(set(results))}"

    except Exception as e:
        return f"⚠️ Erreur Système : {str(e)}"
