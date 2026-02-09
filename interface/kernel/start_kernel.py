import streamlit as st
from supabase import create_client

def get_supabase():
    """Établit la connexion avec votre projet Supabase"""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def delta_memory_save(info, dossier="Général"):
    """
    Sauvegarde flexible : DELTA choisit le dossier (ex: 'Identité', 'Lycée')
    """
    try:
        supabase = get_supabase()
        data = {
            "folder_name": dossier,
            "content": info,
            "metadata": {"status": "memory_active"}
        }
        supabase.table("archives").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erreur de mémoire : {e}")
        return False

def start_DELTA():
    """Initialise l'intelligence de DELTA"""
    st.success("Système DELTA initialisé avec accès Cloud.")
    # C'est ici que l'agent LLM est chargé
