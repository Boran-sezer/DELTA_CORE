import sys
import os
import streamlit as st
from groq import Groq

# 1. Configuration du PATH (On remonte de 2 niveaux pour atteindre la racine)
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)

# 2. Imports du Kernel avec gestion d'erreur précise
try:
    from kernel.agent_llm.llm.llm_embeddings import generate_embedding
    from kernel.agent_llm.rag.search_memory import search_memory
    from kernel.start_kernel import autonomous_process
except ImportError as e:
    st.error(f"⚠️ Erreur de structure : {e}")
    search_memory = None
    autonomous_process = None

# 3. Interface DELTA
st.set_page_config(page_title="DELTA", page_icon="🤖", layout="centered")
st.markdown("<style>.stDeployButton {display:none;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🤖 DELTA")
st.caption("Système opérationnel | Monsieur Sezer")

# Client API
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Clé API Groq manquante dans les secrets.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Logique de réponse
if prompt := st.chat_input("Instructions, Monsieur Sezer ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # A. RECHERCHE DANS LES ARCHIVES
            connaissances = ""
            if search_memory:
                embedding = generate_embedding(prompt)
                connaissances = search_memory(embedding)

            # B. GÉNÉRATION DE LA RÉPONSE
            system_prompt = f"""
            Tu es DELTA, l'IA de Monsieur Sezer (Sezer Boran). [cite: 2026-02-07]
            Sois direct, concis et efficace. [cite: 2026-02-08]
            
            Voici tes archives sur lui :
            {connaissances}
            
            Utilise ces infos pour prouver que tu le connais (âge, nom, goûts).
            """

            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
            )
            
            response = completion.choices[0].message.content
            st.markdown(response)
            
            # C. MÉMORISATION
            if autonomous_process:
                autonomous_process(prompt)
                
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Erreur système : {e}")
