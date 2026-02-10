from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding
import groq # Assurez-vous d'avoir accès à votre client Groq ici
import os

def autonomous_process(prompt, groq_client):
    """
    Traite le message, décide du dossier via Groq, génère un vecteur et sauvegarde.
    """
    try:
        # --- PHASE DE TRI (L'Étape 1) ---
        classification_prompt = f"""
        Tu es l'aiguilleur de DELTA. Analyse cette phrase : "{prompt}"
        Choisis UNIQUEMENT un dossier de rangement parmi ceux-là :
        - Utilisateur/Identite
        - Utilisateur/Preferences
        - Social/Amis
        - Projets/Delta
        - Divers
        Réponds UNIQUEMENT le nom du dossier, sans rien d'autre.
        """
        
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": classification_prompt}],
            model="llama3-8b-8192", # On utilise le modèle rapide pour le tri
        )
        
        smart_path = chat_completion.choices[0].message.content.strip()
        
        # --- PHASE DE SAUVEGARDE ---
        embedding = generate_embedding(prompt)
        
        # On utilise maintenant 'smart_path' au lieu de "Mémoire/Automatique"
        success = save_to_memory(prompt, embedding, smart_path)
        
        if success:
            return f"Connaissance classée dans [{smart_path}]"
        return "Erreur lors de l'écriture en base de données"
        
    except Exception as e:
        return f"Erreur Kernel : {str(e)}"
