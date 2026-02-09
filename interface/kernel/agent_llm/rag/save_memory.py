import streamlit as st
from supabase import create_client

# Initialisation
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def save_to_memory(content, embedding, path):
    try:
        # Transformation du vecteur en format compatible SQL Vector
        # On s'assure que c'est une liste de floats
        formatted_embedding = [float(x) for x in embedding]

        data = {
            "content": str(content),
            "embedding": formatted_embedding, 
            "path": str(path)
        }
        
        # Envoi à Supabase
        response = supabase.table("archives").insert(data).execute()
        
        return True
    except Exception as e:
        # Affiche l'erreur exacte dans l'interface pour le débogage final
        st.error(f"Erreur technique Supabase : {e}")
        return False
