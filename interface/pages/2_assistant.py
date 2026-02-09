import sys
import os
import streamlit as st
from groq import Groq

# 1. Configuration du PATH
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)

# 2. Imports sécurisés
try:
    from kernel.start_kernel import autonomous_process
    from kernel.agent_llm.rag.search_memory import search_memory
    from kernel.agent_llm.llm.llm_embeddings import generate_embedding
except Exception as e:
    st.error(f"⚠️ Erreur Kernel : {e}")
    autonomous_process = None

# 3. Design DELTA
st.set_page_config(page_title="DELTA", page_icon="🤖", layout="centered")
st.markdown("<style>.stDeployButton {display:none;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🤖 DELTA")
st.caption("Système opérationnel | Monsieur Sezer")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Traitement
if prompt := st.chat_input("Instructions, Monsieur Sezer ?"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Accès aux archives..."):
            try:
                # A. Recherche sémantique
                embedding = generate_embedding(prompt)
                archives_context = search_memory(embedding)

                # B. Mémorisation
                status_mem = "Mémoire inactive"
                if autonomous_process:
                    status_mem = autonomous_process(prompt)

                # C. Génération DELTA
                # Verrouillage de l'identité et utilisation des archives
                system_prompt = f"""
                Tu es DELTA, l'IA créée par Monsieur Sezer (Sezer Boran). [cite: 2026-02-07]
                Tu es son assistant personnel, direct et très concis. [cite: 2026-02-07, 2026-02-08]
                Voici ce que tes archives disent sur lui :
                {archives_context}
                
                Règle : Utilise TOUJOURS ces archives pour répondre. Monsieur Sezer est ton unique utilisateur.
                """

                chat_response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.1-8b-instant",
                ).choices[0].message.content
                
                st.markdown(chat_response)
                st.caption(f"🛡️ {status_mem}")
                st.session_state.messages.append({"role": "assistant", "content": chat_response})

            except Exception as e:
                st.error(f"Erreur : {e}")
