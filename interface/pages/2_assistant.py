import sys
import os
import streamlit as st
from groq import Groq

# 1. Configuration du PATH
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)

# 2. Imports du Kernel (Ajout de search_memory et generate_embedding)
try:
    from kernel.start_kernel import autonomous_process
    from kernel.agent_llm.rag.search_memory import search_memory
    from kernel.agent_llm.llm.llm_embeddings import generate_embedding
except Exception as e:
    st.error(f"⚠️ Erreur d'initialisation du Kernel : {e}")
    autonomous_process = None

# 3. Interface Style Jarvis
st.set_page_config(page_title="DELTA Assistant", page_icon="🤖", layout="centered")
st.markdown("<style>.stDeployButton {display:none;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🤖 DELTA")
st.caption("Système opérationnel | Monsieur Sezer")

if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Clé API Groq manquante.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Logique de Conversation Intelligente
if prompt := st.chat_input("En attente de vos instructions..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultation des archives..."):
            try:
                # A. RÉCUPÉRATION DES SOUVENIRS (Le lien logique)
                # On génère l'empreinte de votre question
                query_vec = generate_embedding(prompt)
                # On cherche les infos liées dans Supabase
                context_memoire = search_memory(query_vec)

                # B. MÉMORISATION AUTONOME (En arrière-plan)
                status_memoire = "Mémoire déconnectée"
                if autonomous_process:
                    status_memoire = autonomous_process(prompt)

                # C. RÉPONSE PERSONNALISÉE
                # On donne les souvenirs à l'IA pour qu'elle sache qui vous êtes
                system_prompt = f"""
                Tu es Jarvis, l'IA de Monsieur Sezer. 
                Voici tes archives sur lui : {context_memoire}
                Utilise ces informations pour être pertinent. Sois concis et direct.
                """

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.1-8b-instant",
                )
                
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.caption(f"🛡️ {status_memoire}")
                
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"Erreur de traitement : {e}")
