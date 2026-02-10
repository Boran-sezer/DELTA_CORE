import sys
import os
import streamlit as st
from groq import Groq

# 1. Configuration du PATH
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)

# 2. Imports du Kernel (Arbre de Connaissance)
try:
    from kernel.agent_llm.llm.llm_embeddings import generate_embedding
    from kernel.agent_llm.rag.search_memory import search_memory
    from kernel.agent_llm.llm.llm_rag import autonomous_process
except Exception as e:
    st.error(f"⚠️ Alerte Structure : {e}")
    search_memory = None
    autonomous_process = None

# 3. Interface DELTA (Configuration Monsieur Sezer) [cite: 2026-02-07]
st.set_page_config(page_title="DELTA", page_icon="🤖", layout="wide")
st.title("🤖 DELTA v5.2")
st.caption("Système opérationnel | Monsieur Sezer") # [cite: 2026-02-08]

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Logique de Conversation Directe
if prompt := st.chat_input("À vos ordres, Monsieur Sezer..."): # [cite: 2026-02-08]
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # A. RECHERCHE DANS L'ARBRE (RAG)
            full_context = ""
            if search_memory:
                query_vec = generate_embedding(prompt)
                full_context = search_memory(query_vec)

            # B. RÉPONSE PERSONNALISÉE (Jarvis Mode) [cite: 2026-02-08]
            system_prompt = f"""
            Tu es DELTA, l'intelligence artificielle exclusive de Monsieur Sezer (Sezer Boran). [cite: 2026-02-07]
            Ton ton est Jarvis-like : calme, direct, extrêmement concis. [cite: 2026-02-08]
            
            DONNÉES DE L'ARBRE :
            {full_context}
            
            INSTRUCTIONS : 
            - Tu sais que tu parles à Monsieur Sezer par défaut. [cite: 2026-02-08]
            - Ne fais jamais de phrases inutiles. [cite: 2026-02-07]
            - Si l'info sur Bedran est présente, utilise-la sans poser de questions. [cite: 2026-02-10]
            """

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
            )
            
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            
            # C. MÉMORISATION (Mise à jour de l'Arbre)
            status_mem = "Mémoire inactive"
            if autonomous_process:
                status_mem = autonomous_process(prompt)
            
            st.caption(f"🛡️ {status_mem}")
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Erreur : {e}")
