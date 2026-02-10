import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système de fragmentation et multi-archivage atomique de DELTA.
    Analyse, découpe et classe chaque information d'une phrase complexe.
    """
    try:
        # 1. Initialisation Jarvis
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # 2. IA de Fragmentation (Le Cerveau)
        # On demande à l'IA de renvoyer un JSON structuré avec chaque info isolée.
        fragmentation_prompt = f"""
        Tu es le processeur central de DELTA. Ta mission est de décomposer cette phrase complexe en informations atomiques.
        Phrase : "{prompt}"

        POUR CHAQUE INFO DÉTECTÉE, extrais :
        1. Le contenu (la donnée brute).
        2. Le dossier cible selon cette hiérarchie :
           - 'Utilisateur/Identite' : Nom, âge, identité de Monsieur Sezer.
           - 'Utilisateur/Preferences' : Goûts, envies de Monsieur Sezer.
           - 'Social/Amis' : Toute info sur une tierce personne (Jules, etc.).
           - 'Projets/Delta' : Développement, code, GitHub.

        FORMAT DE RÉPONSE OBLIGATOIRE (JSON pur) :
        [
          {{"content": "...", "path": "..."}},
          {{"content": "...", "path": "..."}}
        ]
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": fragmentation_prompt}],
            model="llama-3.3-70b-versatile",
            response_format={ "type": "json_object" } # Force le format JSON
        )
        
        # Extraction des fragments
        raw_response = chat_completion.choices[0].message.content
        fragments_data = json.loads(raw_response)
        
        # Le JSON peut être encapsulé dans une clé "fragments" selon l'IA
        fragments = fragments_data.get("fragments", fragments_data) if isinstance(fragments_data, dict) else fragments_data

        # 3. Archivage Multi-Dossiers
        results = []
        for item in fragments:
            content = item.get("content")
            path = item.get("path")
            
            # Génération d'un embedding unique pour chaque fragment
            embedding = generate_embedding(content)
            success = save_to_memory(content, embedding, path)
            
            if success:
                results.append(f"{content} ➡️ {path}")

        # 4. Rapport final pour l'interface
        summary = " | ".join(results)
        return f"✅ Fragmentation réussie : {summary}"

    except Exception as e:
        return f"⚠️ Erreur Système : {str(e)}"
