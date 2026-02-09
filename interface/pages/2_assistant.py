import sys
import os
import streamlit as st
from groq import Groq

# Configuration du PATH
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)

# Imports du Kernel
try:
    from kernel.start_kernel import autonomous_process
    from kernel.agent_llm.rag.search_memory import search_memory # Vérifiez le nom ici
    from kernel.agent_llm.llm.llm_embeddings import generate_embedding
except Exception as e:
    st.error(f"⚠️ Erreur d'importation : {e}")
    autonomous_process = None

st.title("🤖 DELTA")
st.caption("Système opérationnel | Monsieur Sezer")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Instructions, Monsieur Sezer ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # A. RECHERCHE DANS LES ARCHIVES
            embedding = generate_embedding(prompt)
            # On récupère ce que DELTA sait (ex: Sezer, 17 ans, Vert)
            connaissances = search_memory(embedding)

            # B. RÉPONSE DE DELTA
            system_prompt = f"""
            Tu es DELTA, l'IA de Monsieur Sezer. [cite: 2026-02-07]
            Tu es direct, concis et efficace. [cite: 2026-02-08]
            Voici tes archives sur Monsieur Sezer :
            {connaissances}
            
            Utilise TOUJOURS ces infos pour prouver que tu le connais.
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
