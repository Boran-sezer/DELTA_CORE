import streamlit as st
from groq import Groq

def generate_embedding(text):
    """Génère des vecteurs via Groq pour la mémoire de DELTA"""
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.embeddings.create(
            model="nomic-embed-text-v1.5",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        st.error(f"Erreur d'initialisation : {e}")
        return None
