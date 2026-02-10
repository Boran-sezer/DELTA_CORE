import streamlit as st
from supabase import create_client

# Initialisation du client Supabase
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def search_memory(query_embedding, limit=5):
    """
    Recherche RAG Intelligence Arborescente.
    Trouve un fait et récupère tout le contexte de la branche associée.
    """
    try:
        # 1. Recherche vectorielle initiale
        rpc_params = {
            'query_embedding': query_embedding,
            'match_threshold': 0.3, # Seuil équilibré pour éviter le "bruit"
            'match_count': limit,
        }
        
        response = supabase.rpc('match_archives', rpc_params).execute()
        
        if not response.data:
            return ""

        # 2. Intelligence de Branche : Récupérer le contexte parent
        # On extrait les chemins (paths) des résultats trouvés
        context_results = []
        for item in response.data:
            path = item.get('path', '')
            content = item.get('content', '')
            
            if path:
                # On remonte d'un cran dans l'arbre (ex: Archives/Social/Famille/Bedran)
                # Cela permet de récupérer TOUTE la fiche de la personne
                parent_path = "/".join(path.split('/')[:-1])
                
                related_data = supabase.table("archives")\
                    .select("content")\
                    .ilike("path", f"{parent_path}%")\
                    .execute()
                
                if related_data.data:
                    for row in related_data.data:
                        context_results.append(row['content'])
            else:
                context_results.append(content)

        # 3. Nettoyage et fusion (supprime les doublons)
        final_context = "\n".join(list(set(context_results)))
        return final_context

    except Exception as e:
        st.error(f"Erreur de recherche (Arbre) : {e}")
        return ""
