import streamlit as st
from supabase import create_client

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def search_memory(query_embedding, limit=5):
    """Interroge la base de données pour trouver des souvenirs pertinents."""
    try:
        rpc_params = {
            'query_embedding': query_embedding,
            'match_threshold': 0.2, # Seuil abaissé pour plus de réactivité
            'match_count': limit,
        }
        
        response = supabase.rpc('match_archives', rpc_params).execute()
        
        if response.data:
            return "\n".join([item['content'] for item in response.data])
        return ""
    except Exception as e:
        print(f"Erreur de recherche : {e}")
        return ""
