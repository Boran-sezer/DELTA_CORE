import sys
import os
import streamlit as st
from groq import Groq

# 1. Configuration du PATH pour lier l'interface au Kernel
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)

# 2. Import sécurisé du processus de mémorisation (Arbre invisible)
try:
    from kernel.start_kernel import autonomous_process
except Exception as e:
    st.error(f"⚠️ Alerte Système : Le Kernel est inaccessible. ({e})")
    autonomous_process = None

# 3. Configuration de l'interface (Style Jarvis)
st.set_page_config(page_title="DELTA Assistant", page_icon="🤖", layout="centered")

# Style CSS pour cacher les éléments inutiles et épurer l'interface
st.markdown("""
    <style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 DELTA")
st.caption("Système opérationnel | Monsieur Sezer")

# 4. Initialisation du client Groq
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Erreur : Clé API Groq introuvable dans les secrets.")

# 5. Gestion de l'historique de conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages passés
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Zone de saisie et Logique de réponse
if prompt := st.chat_input("En attente de vos instructions..."):
    
    # Affichage du message de Monsieur Sezer
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Réponse de l'assistant
    with st.chat_message("assistant"):
        with st.spinner("Traitement..."):
            try:
                # A. MÉMORISATION INVISIBLE (Classement dans l'arbre via LUX)
                status_memoire = "Système de mémoire déconnecté"
                if autonomous_process:
                    status_memoire = autonomous_process(prompt)

                # B. GÉNÉRATION DE LA RÉPONSE IA (Modèle à jour)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", 
                            "content": "Tu es Jarvis, l'IA de Monsieur Sezer. Sois concis, direct et efficace. Réponds toujours en français."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.1-8b-instant",
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                
                # C. LOG DISCRET (Uniquement visible si vous survolez le bas de la réponse)
                # Cela confirme que l'arbre a fonctionné sans polluer l'interface
                st.caption(f"🛡️ {status_memoire}")
                
                # Sauvegarde dans la session
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"Une erreur est survenue lors de la communication : {e}")
