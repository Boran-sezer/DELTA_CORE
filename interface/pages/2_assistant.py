import streamlit as st
from groq import Groq
from kernel.start_kernel import autonomous_process

# 1. Configuration du client Chat
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def get_delta_response(user_input):
    # A. DELTA utilise sa mémoire autonome (Filtrage LUX)
    memory_status = autonomous_process(user_input) 
    
    # B. DELTA prépare sa réponse avec l'IA
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Tu es Jarvis, l'IA de Monsieur Sezer. Sois concis."},
            {"role": "user", "content": user_input}
        ],
        model="llama3-8b-8192", # Ou votre modèle préféré
    )
    
    response = chat_completion.choices[0].message.content
    return response, memory_status

# 2. Affichage dans Streamlit
prompt = st.chat_input("Dites quelque chose à DELTA...")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
        
    response, status = get_delta_response(prompt)
    
    with st.chat_message("assistant"):
        st.markdown(response)
        st.caption(f"🛡️ Statut mémoire : {status}")
