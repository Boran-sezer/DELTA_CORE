import sys
import os
import streamlit as st
from groq import Groq

# 1. Configuration du chemin (PATH) pour trouver le dossier kernel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 2. Imports des fonctions DELTA
try:
    from kernel.start_kernel import autonomous_process
except ImportError as e:
    st.error(f"Erreur d'importation : {e}. Vérifiez la structure de vos dossiers.")

# 3. Configuration de l'interface Streamlit
st.set_page_config(page_title="DELTA Assistant", page_icon="🤖")
st.title("🤖 DELTA - Assistant Intelligent")

# 4. Initialisation du client Groq avec votre clé sécurisée [cite: 2026-02-08]
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 5. Gestion de l'historique de discussion
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages existants
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Boucle de discussion principale
if prompt := st.chat_input("Monsieur Sezer, comment puis-je vous aider ?"):
    # Affichage du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # A. Phase de Mémoire Autonome (Logique LUX)
    with st.spinner("Analyse sémantique et mémorisation..."):
        memory_status = autonomous_process(prompt)

    # B. Phase de Réponse IA via Groq
    with st.chat_message("assistant"):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Tu es Jarvis, l'IA de Monsieur Sezer. Sois concis, direct et efficace."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192", # Modèle ultra-rapide
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            
            # Petit indicateur de l'action mémoire en bas de réponse
            st.caption(f"🛡️ {memory_status}")
            
            # Sauvegarde de la réponse dans l'historique
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Erreur de communication avec l'IA : {e}")
