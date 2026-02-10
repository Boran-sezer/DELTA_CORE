import streamlit as st
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système de tri intelligent de DELTA.
    Utilise le nouveau modèle Llama 3.3 pour éviter l'erreur 400.
    """
    try:
        # 1. Récupération du client Groq (via argument ou Secrets)
        groq_client = kwargs.get('groq_client')
        if groq_client is None:
            api_key = st.secrets["GROQ_API_KEY"]
            groq_client = Groq(api_key=api_key)
        
        # 2. Détermination du dossier (Classification)
        # CHANGEMENT : Utilisation de llama-3.3-70b-versatile
        classification_prompt = f"""
        Tu es l'aiguilleur de DELTA. Analyse cette phrase : "{prompt}"
        Choisis UNIQUEMENT un dossier de rangement parmi :
        - Utilisateur/Identite
        - Utilisateur/Preferences
        - Social/Amis
        - Projets/Delta
        - Divers
        Réponds UNIQUEMENT le nom du dossier.
        """
        
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": classification_prompt}],
            model="llama-3.3-70b-versatile",
        )
        
        smart_path = chat_completion.choices[0].message.content.strip()
        
        # 3. Génération de l'embedding et Sauvegarde
        embedding = generate_embedding(prompt)
        success = save_to_memory(prompt, embedding, smart_path)
        
        if success:
            return f"✅ Info classée dans : {smart_path}"
        return "❌ Erreur de sauvegarde dans la table archives."
        
    except Exception as e:
        return f"⚠️ Erreur Kernel : {str(e)}"
