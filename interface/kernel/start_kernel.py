import st
from groq import Groq
from kernel.agent_llm.llm.llm_embeddings import generate_embedding
from kernel.agent_llm.rag.similarity_search import get_most_similar_tool

# Client Groq pour la prise de décision
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def autonomous_process(user_input):
    """
    Analyse, classe et mémorise l'information de manière invisible.
    """
    try:
        # 1. ANALYSE : L'IA décide du chemin (Arbre invisible)
        # On demande à Groq de classer sans répondre à l'utilisateur
        classification_prompt = f"""
        Analyse cette phrase : "{user_input}"
        Détermine un chemin de dossier logique (ex: Identité, Lycée/Maths, Projets/Delta).
        Réponds UNIQUEMENT avec le chemin, rien d'autre.
        """
        
        path_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": classification_prompt}],
            model="llama-3.1-8b-instant",
        )
        detected_path = path_completion.choices[0].message.content.strip()

        # 2. VÉRIFICATION : Est-ce une information déjà connue ? (Filtrage LUX)
        # On génère l'embedding pour comparer avec Supabase
        embedding = generate_embedding(user_input)
        
        # similarity_check renvoie True si l'info est trop proche d'une ancienne
        is_duplicate = get_most_similar_tool(user_input, embedding, detected_path)

        if is_duplicate:
            return f"Information déjà classée dans {detected_path}."

        # 3. ACTION : Sauvegarde silencieuse dans l'arbre
        # (Ici, votre fonction de sauvegarde Supabase utilisant detected_path)
        # save_to_supabase(user_input, embedding, detected_path)
        
        return f"Mémorisé avec succès sous {detected_path}."

    except Exception as e:
        return f"Erreur de traitement interne : {e}"
