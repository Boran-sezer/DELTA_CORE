import sys
import os
import streamlit as st
from groq import Groq

# 1. Configuration du PATH pour atteindre la racine DELTA_CORE
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)

# 2. Imports du Kernel
try:
    # On importe les 3 piliers de la mémoire
    from kernel.agent_llm.llm.llm_embeddings import generate_embedding
    from kernel.agent_llm.rag.search_memory import search_memory
    from kernel.start_kernel import autonomous_process
except Exception as e:
    st.error(f"⚠️ Alerte Structure : {e}")
    search_memory = None
    autonomous_process = None

# 3. Configuration Interface
st.set_page_config(page_title="DELTA", page_icon="🤖")
st.title("🤖 DELTA")
st.caption("Système opérationnel | Monsieur Sezer")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Logique de Conversation
if prompt := st.chat_input("Instructions, Monsieur Sezer ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # A. RECHERCHE SÉMANTIQUE (Lecture des archives)
            archives = ""
            if search_memory:
                query_vec = generate_embedding(prompt)
                archives = search_memory(query_vec)

            # B. RÉPONSE PERSONNALISÉE
            system_prompt = f"""
            Tu es DELTA, l'IA de Monsieur Sezer (Sezer Boran). [cite: 2026-02-07]
            Sois direct, concis et Jarvis-like. [cite: 2026-02-08]
            
            Voici ce que tu sais sur lui (Archives) :
            {archives}
            
            Utilise ces infos pour répondre. Si l'info n'est pas là, ne l'invente pas.
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
            
            # C. MÉMORISATION (Écriture invisible)
            status_mem = "Mémoire inactive"
            if autonomous_process:
                status_mem = autonomous_process(prompt)
            
            st.caption(f"🛡️ {status_mem}")
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Erreur lors du traitement : {e}")
