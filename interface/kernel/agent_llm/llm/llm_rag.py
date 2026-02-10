import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v4.0 : Archivage par Synthèse d'Entités.
    Empêche la fragmentation et fusionne les faits.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Bloque la pollution) ---
        filter_prompt = f"Analyse : '{prompt}'. Si c'est une info sur la vie (nom, âge, lien), réponds 'MEMO'. Sinon 'IGNORE'."
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant"
        )
        
        if "IGNORE" in check_task.choices[0].message.content.upper():
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : L'ARCHIVISTE (Synthèse complète) ---
        # On utilise le 70b pour une rédaction parfaite des fiches. [cite: 2026-02-10]
        synth_prompt = f"""
        Tu es l'archiviste de Monsieur Sezer. Transforme ce texte en FICHES D'IDENTITÉ complètes : "{prompt}"
        
        RÈGLES D'OR :
        1. UNE LIGNE = UNE PERSONNE. Fusionne le nom, l'âge et le lien (ex: "Bedran est le grand frère de Sezer et a 26 ans").
        2. NE DÉCOUPE PAS les faits en petits morceaux. [cite: 2026-02-10]
        3. IGNORE les chiffres seuls comme "7" ou les mots isolés.
        
        STRUCTURE :
        - 'Social/Famille/[Nom]'
        - 'Utilisateur/Identite' (Si c'est Sezer)
        
        RÉPONDS UNIQUEMENT EN JSON :
        {{ "fragments": [ {{"content": "La fiche complète ici", "path": "Le chemin ici"}} ] }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": synth_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        data = json.loads(chat_completion.choices[0].message.content)
        fragments = data.get("fragments", [])
        results = []

        # --- SAUVEGARDE ET VALIDATION ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # Sécurité : On ignore les déchets (ID 67 de votre capture)
            if len(content.split()) < 4: 
                continue
                
            embedding = generate_embedding(content)
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Synthèse réussie : {', '.join(set(results))}" if results else "Pollution ignorée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
