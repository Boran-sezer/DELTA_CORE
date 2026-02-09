import requests
import streamlit as st
from CONFIG import *

# Remplacez par votre token Hugging Face dans les Secrets de Streamlit
HF_TOKEN = st.secrets["HF_TOKEN"]
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

def generate_embedding(text):
    """
    Génère des embeddings via l'API gratuite de Hugging Face.
    Remplace Ollama pour le fonctionnement Cloud de DELTA.
    """
    api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{MODEL_ID}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        response = requests.post(api_url, headers=headers, json={"inputs": text})
        
        if response.status_code == 200:
            # L'API renvoie directement une liste de flottants (le vecteur)
            return response.json()
        else:
            st.error(f"Erreur API Hugging Face : {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None
