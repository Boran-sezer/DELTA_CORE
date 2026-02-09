from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt):
    """
    Traite le message pour générer un embedding et le sauvegarder.
    """
    try:
        # Génération du vecteur
        embedding = generate_embedding(prompt)
        
        # Sauvegarde dans Supabase
        # Le path peut être adapté selon vos besoins futurs
        success = save_to_memory(prompt, embedding, "Mémoire/Automatique")
        
        if success:
            return "Nouvelle connaissance acquise"
        return "Erreur lors de l'écriture en base de données"
        
    except Exception as e:
        return f"Erreur Kernel : {str(e)}"
