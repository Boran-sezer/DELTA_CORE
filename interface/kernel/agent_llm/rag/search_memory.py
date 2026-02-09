import streamlit as st
from supabase import create_client

# Connexion sécurisée
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def search_memory(query_embedding, limit=5):
    """
    Interroge la base de données pour trouver des souvenirs similaires.
    """
    try:
        # Paramètres pour la fonction SQL match_archives que vous avez créée
        rpc_params = {
            'query_embedding': query_embedding,
            'match_threshold': 0.4, # Sensibilité de la recherche
            'match_count': limit,
        }
        
        # Appel de la fonction de recherche sémantique dans Supabase
        response = supabase.rpc('match_archives', rpc_params).execute()
        
        if response.data:
            # On fusionne les résultats pour donner du contexte à l'IA
            context = "\n".join([item['content'] for item in response.data])
            return context
        return ""
        
    except Exception as e:
        print(f"Erreur lors de la recherche mémoire : {e}")
        return ""
