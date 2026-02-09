import streamlit as st
import sys
import os
import importlib.util

# Définition du chemin vers le module de construction
current_dir = os.path.dirname(os.path.abspath(__file__))
path_to_auto_build = os.path.join(current_dir, "agent_llm", "build_llm", "auto_build_llm.py")

def load_agent_module():
    """Charge dynamiquement le module auto_build_llm."""
    if not os.path.exists(path_to_auto_build):
        st.error(f"Fichier introuvable : {path_to_auto_build}")
        return None
    
    spec = importlib.util.spec_from_file_location("agent_core", path_to_auto_build)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def start_DELTA():
    """Lance l'interface de discussion Jarvis."""
    
    # Initialisation du module et de la classe
    agent_mod = load_agent_module()
    if not agent_mod:
        return

    # Gestion de l'instance dans le session_state
    if "agent_instance" not in st.session_state:
        st.session_state.agent_instance = agent_mod.DELTA_Agent()
    
    if "session_state" not in st.session_state:
        st.session_state.session_state = []

    # --- AFFICHAGE DE L'INTERFACE DE CHAT ---
    for message in st.session_state.session_state:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("En quoi puis-je vous aider, Monsieur Sezer ?"):
        # Message Utilisateur
        st.session_state.session_state.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Réponse Assistant
        with st.chat_message("assistant"):
            with st.spinner("DELTA réfléchit..."):
                response = st.session_state.agent_instance.chat(prompt)
                st.markdown(response)
                
                # Optionnel : Ajoutez ici votre appel à la voix si nécessaire
        
        st.session_state.session_state.append({"role": "assistant", "content": response})

    # Bouton de secours pour reconstruire l'identité
    if st.sidebar.button("🔄 Réinitialiser l'identité"):
        if agent_mod.build_the_model():
            st.sidebar.success("Identité mise à jour, Monsieur Sezer.")
            st.rerun()