import streamlit as st
from groq import Groq
from kernel.agent_llm.llm.llm_embeddings import generate_embedding
from kernel.agent_llm.rag.similarity_search import get_most_similar_tool
from kernel.agent_llm.rag.save_memory import save_to_memory

# Client Groq pour la décision de classification
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def get_ai_path(user_input):
    """Demande à l'IA de classer l'info dans un dossier logique (Arbre Invisible)"""
    prompt = f"""
    Tu es le système de classement de DELTA.
    Analyse cette info : "{user_input}"
    Détermine un chemin de dossier (ex: Lycée/Amis, Identité/Préférences, Projets/Delta).
    Réponds uniquement avec le chemin.
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        return completion.choices[0].message.content.strip()
    except:
        return "Général"

def autonomous_process(user_input):
    """Processus complet de mémorisation autonome"""
    try:
        # 1. Classification (Arbre)
        path = get_ai_path(user_input)
        
        # 2. Empreinte numérique
        embedding = generate_embedding(user_input)
        
        # 3. Filtrage LUX (Doublons dans ce dossier)
        is_duplicate = get_most_similar_tool(user_input, embedding, path)
        
        if is_duplicate:
            return f"Information déjà connue (Chemin : {path})"
        
        # 4. Sauvegarde via le nouveau fichier save_memory.py
        success = save_to_memory(user_input, embedding, path)
        
        if success:
            return f"Nouvelle connaissance acquise : {path}"
        return "Erreur lors de l'écriture en base de données."

    except Exception as e:
        return f"Erreur système : {str(e)}"
