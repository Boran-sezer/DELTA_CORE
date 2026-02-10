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
            # A. RECHERCHE RAG ARBORESCENTE (Multi-Query + Path Exploration)
            full_context = ""
            if search_memory:
                # Agent de raffinement : identifie les branches potentielles à explorer
                refiner = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Pour : '{prompt}', donne 3 chemins de dossiers probables (ex: Archives/Social/Famille) et 2 mots-clés, séparés par des virgules."}],
                    model="llama-3.1-8b-instant",
                )
                keywords = refiner.choices[0].message.content.split(',')
                search_terms = [prompt] + [k.strip() for k in keywords]
                
                context_results = []
                for term in search_terms:
                    query_vec = generate_embedding(term)
                    res = search_memory(query_vec)
                    if res:
                        context_results.append(res)
                
                # Fusion unique pour éviter les répétitions
                full_context = "\n".join(list(set(context_results)))

            # B. RÉPONSE JARVIS (Synthèse de l'Arbre)
            system_prompt = f"""
            Tu es DELTA, l'intelligence de Monsieur Sezer (Sezer Boran). [cite: 2026-02-07]
            Ton ton est direct, concis et Jarvis-like. [cite: 2026-02-08]
            
            BRANCHES DE MÉMOIRE EXPLORÉES :
            {full_context}
            
            CONSIGNES :
            1. Utilise les fragments pour répondre avec certitude.
            2. Si un nom (ex: Bedran) est lié à une relation (ex: Frère) dans l'arbre, fusionne l'info. [cite: 2026-02-10]
            3. Ne mentionne pas que tu cherches dans tes dossiers, réponds naturellement.
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
            
            # C. MÉMORISATION (Mise à jour de l'Arbre Infini)
            status_mem = "Mémoire inactive"
            if autonomous_process:
                status_mem = autonomous_process(prompt)
            
            st.caption(f"🛡️ {status_mem}")
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Erreur de traitement : {e}")
