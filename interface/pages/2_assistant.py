import sys
import os
import streamlit as st
from groq import Groq

# 1. Configuration du PATH
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)

# 2. Imports du Kernel
try:
    from kernel.agent_llm.llm.llm_embeddings import generate_embedding
    from kernel.agent_llm.rag.search_memory import search_memory
    from kernel.agent_llm.llm.llm_rag import autonomous_process
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
            # A. RECHERCHE RAG OPTIMISÉE (Multi-Pass)
            context_list = []
            if search_memory:
                # Premier passage : Recherche sur la phrase entière
                query_vec = generate_embedding(prompt)
                context_list.append(search_memory(query_vec))
                
                # Second passage : Recherche sur les noms propres (si présents)
                # On divise la phrase pour chercher chaque mot capitalisé (noms)
                for word in prompt.split():
                    if word[0].isupper() or len(word) > 4:
                        word_vec = generate_embedding(word)
                        context_list.append(search_memory(word_vec))
            
            # Fusion unique du contexte
            full_context = "\n".join(list(set(context_list)))

            # B. RÉPONSE PERSONNALISÉE (Mode Jarvis)
            system_prompt = f"""
            Tu es DELTA, l'IA de Monsieur Sezer. [cite: 2026-02-07]
            Sois direct, concis et Jarvis-like. [cite: 2026-02-08]
            
            ARCHIVES RETROUVÉES :
            {full_context}
            
            CONSIGNE : Utilise ces fragments pour répondre précisément. 
            Si tu vois un nom et un âge séparés, fais le lien. [cite: 2026-02-10]
            """

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile", # Modèle plus puissant pour le RAG
            )
            
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            
            # C. MÉMORISATION (Fragmentation Atomique)
            status_mem = "Mémoire inactive"
            if autonomous_process:
                status_mem = autonomous_process(prompt)
            
            st.caption(f"🛡️ {status_mem}")
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Erreur : {e}")
