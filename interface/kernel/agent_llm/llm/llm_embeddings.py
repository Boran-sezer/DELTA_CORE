from sentence_transformers import SentenceTransformer

# Initialisation du modèle (chargé une seule fois en cache)
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text):
    """
    Génère un vecteur numérique (embedding) pour le texte donné.
    """
    try:
        # Génération du vecteur
        embedding = model.encode(text)
        # Conversion en liste pour Supabase
        return embedding.tolist()
    except Exception as e:
        print(f"Erreur d'embedding : {e}")
        return None
