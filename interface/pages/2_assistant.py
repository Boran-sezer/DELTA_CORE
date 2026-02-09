import sys
import os
import streamlit as st
from groq import Groq

# 1. Configuration du chemin (PATH) pour trouver le dossier kernel
# Cela permet d'importer des modules depuis la racine du projet DELTA_CORE
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 2. Imports sécurisés des fonctions DELTA
try:
    from kernel.start_kernel import autonomous_process
except ImportError:
    st.error("⚠️ Erreur : Structure de dossiers incorrecte ou kernel/start_kernel.py introuvable.")
    autonomous_process = lambda x: "Erreur d'importation"

# 3. Configuration de l'interface Streamlit
st.set_page_config(page_title="DELTA Assistant", page_icon="🤖", layout="centered")
st.title("🤖 DELTA - Assistant")
st.markdown("---")

# 4. Initialisation du client Groq (Clé récupérée dans les Secrets Streamlit)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Clé API Groq manquante dans les Secrets Streamlit.")

# 5. Gestion de l'historique de discussion (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages de la session
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Zone de saisie et logique principale
if prompt := st.chat_input("Monsieur Sezer, je vous écoute..."):
    
    # A. Affichage du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # B. Traitement par l'IA
    with st.chat_message("assistant"):
        # Animation de chargement
        with st.spinner("Analyse et réponse en cours..."):
            try:
                # 1. Phase de Mémoire Autonome (Filtrage LUX)
                memory_status = autonomous_process(prompt)

                # 2. Appel à la nouvelle API Groq (Modèle Llama 3.1)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", 
                            "content": "Tu es Jarvis, l'IA de Monsieur Sezer. Tu es concis, direct, poli et efficace. Réponds toujours en français."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.1-8b-instant", # Modèle à jour
                    temperature=0.7,
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                
                # 3. Affichage du statut de la mémoire en bas de réponse
                st.caption(f"🛡️ **Système LUX :** {memory_status}")
                
                # Sauvegarde de la réponse
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")
