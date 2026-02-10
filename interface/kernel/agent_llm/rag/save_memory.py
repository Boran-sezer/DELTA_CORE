import streamlit as st
from supabase import create_client

# Initialisation
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def save_to_memory(content, embedding, path):
    """
    Sauvegarde avec écrasement automatique (Upsert) basé sur le chemin unique.
    """
    try:
        # Transformation du vecteur en format compatible SQL Vector
        formatted_embedding = [float(x) for x in embedding]

        data = {
            "content": str(content),
            "embedding": formatted_embedding, 
            "path": str(path)
        }
        
        # --- CORRECTION CRITIQUE : UPSERT ---
        # on_conflict='path' force Supabase à mettre à jour la ligne si le path existe déjà.
        # Cela utilise la contrainte UNIQUE que nous avons posée en SQL. [cite: 2026-02-10]
        response = supabase.table("archives").upsert(data, on_conflict='path').execute()
        
        return True
    except Exception as e:
        # Affiche l'erreur exacte pour le débogage, utile pour voir si la contrainte bloque.
        st.error(f"Erreur technique Supabase : {e}")
        return False
