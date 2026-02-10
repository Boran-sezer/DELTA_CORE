import streamlit as st
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système de tri intelligent de DELTA.
    Version 'Priorité Entités' pour Monsieur Sezer.
    """
    try:
        # 1. Connexion au client Groq (via Secrets Streamlit)
        # On utilise le bouclier *args, **kwargs pour ignorer les envois superflus de l'interface.
        groq_client = kwargs.get('groq_client')
        if groq_client is None:
            api_key = st.secrets["GROQ_API_KEY"]
            groq_client = Groq(api_key=api_key)
        
        # 2. IA Aiguilleur - Instructions de tri avec Hiérarchie de Décision
        # Le modèle 70b est utilisé pour sa capacité supérieure à distinguer 'Moi' des 'Autres'.
        classification_prompt = f"""
        Tu es l'expert en archivage de DELTA. Ton rôle est de classer cette info : "{prompt}"
        
        HIÉRARCHIE DE DÉCISION (Très important) :
        1. PRIORITÉ SOCIALE : Si la phrase mentionne un nom tiers (Jules, Paul, etc.) ou un lien social (ami, pote, frère, collègue), choisis : Social/Amis.
        2. PROJETS : Si la phrase parle de code, de GitHub ou du développement de DELTA, choisis : Projets/Delta.
        3. IDENTITÉ : Si la phrase parle UNIQUEMENT de Monsieur Sezer (son nom, son âge, son identité propre), choisis : Utilisateur/Identite.
        4. PRÉFÉRENCES : Si cela concerne les goûts (j'aime, je déteste) de Monsieur Sezer, choisis : Utilisateur/Preferences.
        
        Réponds UNIQUEMENT le nom du dossier parmi cette liste :
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
        
        # Nettoyage strict du résultat pour Supabase
        smart_path = chat_completion.choices[0].message.content.strip()
        smart_path = smart_path.replace('"', '').replace("'", "")
        
        # 3. Génération de l'embedding et Sauvegarde dans la table 'archives'
        # On transforme la phrase en vecteur pour permettre la recherche future (RAG).
        embedding = generate_embedding(prompt)
        success = save_to_memory(prompt, embedding, smart_path)
        
        if success:
            return f"✅ Info classée dans : {smart_path}"
        return "❌ Erreur de sauvegarde dans la table archives."
        
    except Exception as e:
        # Retourne l'erreur directement dans le caption de l'interface pour diagnostic.
        return f"⚠️ Erreur Kernel : {str(e)}"
