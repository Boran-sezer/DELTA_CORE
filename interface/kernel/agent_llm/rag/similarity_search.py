import streamlit as st
from supabase import create_client
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Connexion à Supabase
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def get_most_similar_tool(user_input, user_embedding, detected_path):
    """
    Vérifie si une information similaire existe déjà dans un dossier spécifique.
    """
    try:
        # 1. RÉCUPÉRATION : On ne cherche que dans le dossier 'detected_path'
        # Cela évite de mélanger les infos du Lycée avec l'Identité
        response = supabase.table("archives") \
            .select("content, embedding") \
            .eq("path", detected_path) \
            .execute()

        if not response.data:
            return False # Dossier vide, donc pas de doublon

        # 2. COMPARAISON MATHÉMATIQUE (Sklearn)
        existing_embeddings = [np.array(row['embedding']) for row in response.data]
        user_vec = np.array(user_embedding).reshape(1, -1)

        # Calcul de la similarité
        similarities = cosine_similarity(user_vec, existing_embeddings)[0]
        max_similarity = max(similarities)

        # 3. SEUIL DE TOLÉRANCE (0.85 = Très similaire)
        # Si le score est élevé, DELTA considère qu'il connaît déjà l'info
        if max_similarity > 0.85:
            return True
        
        return False

    except Exception as e:
        print(f"Erreur de recherche : {e}")
        return False
