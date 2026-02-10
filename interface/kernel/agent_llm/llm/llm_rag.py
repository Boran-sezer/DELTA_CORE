import streamlit as st
import json
from groq import Groq
from kernel.agent_llm.rag.save_memory import save_to_memory
from kernel.agent_llm.llm.llm_embeddings import generate_embedding

def autonomous_process(prompt, *args, **kwargs):
    """
    Système DELTA v6.0 : Master Archivage Monsieur Sezer.
    Forçage systématique des faits personnels sans exception.
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        groq_client = Groq(api_key=api_key)
        
        # --- AGENT 1 : LE FILTRE (Priorité Absolue) ---
        # On force l'IA à voir chaque répétition comme une nouvelle commande [cite: 2026-02-10]
        filter_prompt = f"""
        ANALYSE CRITIQUE : "{prompt}"
        Si la phrase contient : âge, nom, préférence, goût ou famille de Monsieur Sezer, 
        réponds EXCLUSIVEMENT 'MEMO' peu importe si c'est une répétition ou non. [cite: 2026-02-10]
        Réponse unique : 'MEMO' ou 'IGNORE'.
        """
        
        check_task = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": filter_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0
        )
        
        decision = check_task.choices[0].message.content.upper()
        
        if "MEMO" not in decision:
            return "Interaction simple (non archivée)"

        # --- AGENT 2 : LE CARTOGRAPHE (Tiroirs Rigides v2) ---
        # On impose des chemins fixes sans aucune variante possible [cite: 2026-02-10]
        tree_prompt = f"""
        Tu es le cartographe. Donnée : "{prompt}"
        
        TIROIRS FIXES IMPOSÉS (Strict) :
        1. Archives/Utilisateur/Identite/Age
        2. Archives/Utilisateur/Gouts/Alimentaire
        3. Archives/Utilisateur/Famille/Composition
        
        RÈGLE : Si l'utilisateur exprime un goût, utilise TOUJOURS le tiroir n°2. [cite: 2026-02-10]
        
        RÉPONDS EN JSON :
        {{ "fragments": [ {{"content": "Monsieur Sezer + fait complet", "path": "Le chemin choisi"}} ] }}
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": tree_prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        data = json.loads(chat_completion.choices[0].message.content)
        fragments = data.get("fragments", [])
        results = []

        # --- SAUVEGARDE DIRECTE ---
        for item in fragments:
            content, path = item.get("content"), item.get("path")
            
            # Plus aucune barrière de sécurité sur la longueur, on enregistre tout [cite: 2026-02-10]
            embedding = generate_embedding(content)
            
            if save_to_memory(content, embedding, path):
                results.append(path)

        return f"Arbre mis à jour : {', '.join(set(results))}" if results else "Branche rejetée."

    except Exception as e:
        return f"Erreur Système : {str(e)}"
