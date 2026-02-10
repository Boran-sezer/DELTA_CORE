import streamlit as st
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système de tri intelligent de DELTA.
    Version 'Anti-Confusion' pour Monsieur Sezer.
    """
    try:
        # 1. Connexion au client Groq
        groq_client = kwargs.get('groq_client')
        if groq_client is None:
            api_key = st.secrets["GROQ_API_KEY"]
            groq_client = Groq(api_key=api_key)
        
        # 2. IA Aiguilleur - Instructions de tri renforcées
        classification_prompt = f"""
        Tu es l'expert en archivage de DELTA. Ton rôle est de classer cette info : "{prompt}"
        
        RÈGLES DE TRI STRICTES :
        - 'Utilisateur/Identite' : Si l'info parle DIRECTEMENT de Monsieur Sezer (nom, âge de Sezer, identité).
        - 'Utilisateur/Preferences' : Si l'info parle des goûts de Monsieur Sezer (ce qu'il aime/déteste).
        - 'Social/Amis' : Si l'info mentionne une TIERCE PERSONNE (ami, pote, nom comme Jules, Paul, etc.).
        - 'Projets/Delta' : Si l'info parle de code, de développement ou du système DELTA lui-même.
        
        Réponds UNIQUEMENT le nom du dossier parmi :
        - Utilisateur/Identite
        - Utilisateur/Preferences
        - Social/Amis
        - Projets/Delta
        - Divers
        """
        
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": classification_prompt}],
            model="llama-3.3-70b-versatile",
        )
        
        smart_path = chat_completion.choices[0].message.content.strip()
        
        # Nettoyage de la réponse (au cas où l'IA mettrait des guillemets)
        smart_path = smart_path.replace('"', '').replace("'", "")
        
        # 3. Génération de l'embedding et Sauvegarde Supabase
        embedding = generate_embedding(prompt)
        success = save_to_memory(prompt, embedding, smart_path)
        
        if success:
            return f"✅ Info classée dans : {smart_path}"
        return "❌ Erreur de sauvegarde dans la table archives."
        
    except Exception as e:
        return f"⚠️ Erreur Kernel : {str(e)}"
