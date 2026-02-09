import sys
import os
import streamlit as st
from groq import Groq

# 1. Configuration du chemin pour le noyau (Kernel)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 2. Imports des fonctions système
try:
    from kernel.start_kernel import autonomous_process
except ImportError:
    st.error("Système de mémorisation indisponible.")
    autonomous_process = lambda x: "Erreur Système"

# 3. Configuration de l'interface minimaliste
st.set_page_config(page_title="DELTA Assistant", page_icon="🤖", layout="centered")
st.title("🤖 DELTA")

# 4. Initialisation des clients (Secrets Streamlit)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Clé API Groq manquante.")

# 5. Historique de session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage fluide de la conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Boucle d'interaction
if prompt := st.chat_input("Monsieur Sezer..."):
    
    # Affichage immédiat du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Réponse de l'assistant
    with st.chat_message("assistant"):
        try:
            # TRAITEMENT INVISIBLE : Organisation de l'arbre en arrière-plan
            # autonomous_process décide seul du chemin (ex: Lycée/Maths) sans le montrer
            memory_status = autonomous_process(prompt)

            # GÉNÉRATION DE LA RÉPONSE
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es Jarvis, l'IA de Monsieur Sezer. Tu es concis, direct et efficace. Tu gères ta propre mémoire en silence."
                    },
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
            )
            
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            
            # Sauvegarde silencieuse
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Erreur de communication : {e}")
