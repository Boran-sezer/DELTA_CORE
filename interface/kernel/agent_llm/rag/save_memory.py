import streamlit as st
from supabase import create_client

# Connexion sécurisée à votre base de données
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def save_to_memory(content, embedding, path):
    """
    Enregistre une nouvelle information dans l'arbre invisible de Supabase.
    """
    try:
        data = {
            "content": content,
            "embedding": embedding,
            "path": path, # Le dossier invisible choisi par l'IA
        }
        
        # Insertion dans la table 'archives'
        response = supabase.table("archives").insert(data).execute()
        
        return True if response.data else False

    except Exception as e:
        print(f"Erreur de sauvegarde Supabase : {e}")
        return False
