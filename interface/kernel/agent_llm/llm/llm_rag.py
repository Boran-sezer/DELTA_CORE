import streamlit as st
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, groq_client=None):
    """
    Système de tri intelligent pour classer les infos dans Supabase.
    """
    try:
        # Récupération automatique de la clé API dans les Secrets
        if groq_client is None:
            api_key = st.secrets["GROQ_API_KEY"]
            groq_client = Groq(api_key=api_key)
        
        # --- PHASE DE TRI ---
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
            model="llama3-8b-8192",
        )
        
        smart_path = chat_completion.choices[0].message.content.strip()
        
        # --- PHASE DE SAUVEGARDE ---
        embedding = generate_embedding(prompt)
        # On utilise la table 'archives' identifiée dans votre Supabase
        success = save_to_memory(prompt, embedding, smart_path)
        
        if success:
            return f"✅ Info classée dans : {smart_path}"
        return "❌ Erreur de sauvegarde dans la table archives."
        
    except Exception as e:
        return f"⚠️ Erreur Kernel : {str(e)}"
