# ================================================================
# DELTA OS - Interface Streamlit v2.1 (Vocal & Memory Fix)
# ================================================================

import streamlit as st
from groq import Groq
from delta_memory_system import DeltaMemorySystem
import time

# ================================================================
# CONFIG STREAMLIT
# ================================================================

st.set_page_config(
    page_title="Delta OS - JARVIS Edition",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Style custom JARVIS
st.markdown("""
<style>
    [data-testid='stSidebar'] {background-color: #0f0f1e; border-right: 1px solid #1f1f3e;}
    header {display:none}
    .main {background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);}
    .stChatMessage {background: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; border-left: 3px solid #00d4ff;}
</style>
""", unsafe_allow_html=True)

# ================================================================
# INITIALISATION
# ================================================================

st.markdown("# 🔷 Delta OS - JARVIS Protocol v2.1")
st.caption("Active Memory System + Vocal Interface")

if "memory" not in st.session_state:
    with st.spinner("🧠 Initialisation du système de mémoire..."):
        try:
            st.session_state.memory = DeltaMemorySystem()
            st.toast("✅ Système de mémoire activé", icon="🧠")
        except Exception as e:
            st.error(f"❌ Erreur initialisation : {e}")
            st.stop()

memory = st.session_state.memory

if "groq_client" not in st.session_state:
    st.session_state.groq_client = Groq(api_key=st.secrets["groq"]["api_key"])

groq_client = st.session_state.groq_client

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🔷 Système JARVIS v2.1 activé. Prêt à graver vos instructions dans le marbre, Monsieur Sezer."}
    ]

# ================================================================
# AFFICHAGE HISTORIQUE
# ================================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ================================================================
# CHAT INPUT & VOCAL
# ================================================================

# On ajoute une colonne pour le bouton micro (Simulation pour l'instant)
col_input, col_vocal = st.columns([0.9, 0.1])

with col_vocal:
    if st.button("🎤", help="Activer le mode vocal"):
        st.info("Module Whisper en attente...")

if user_input := st.chat_input("Monsieur ?"):
    
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    start_time = time.time()
    
    # 🧠 TRAITEMENT MÉMOIRE (Force l'extraction sémantique)
    with st.spinner("🧠 Gravure en mémoire..."):
        memory_result = memory.process_message(user_input)
    
    if memory_result.get('memories_extracted'):
        st.toast(f"💾 {len(memory_result['memories_extracted'])} nouveau(x) souvenir(s) enregistré(s)", icon="🧠")
    
    # 🔍 RÉCUPÉRATION CONTEXTE
    relevant_entities = memory_result.get('entities', [])
    context = memory.get_contextual_memory(
        query=user_input,
        relevant_entities=relevant_entities
    )
    
    # 🤖 GÉNÉRATION RÉPONSE
    system_instructions = f"""
    Tu es JARVIS, l'IA de Monsieur Sezer (Boran).
    CONTEXTE MÉMOIRE : {context}
    DIRECTIVES : Réponse concise, ton Jarvisien, utilise "Monsieur" et tes souvenirs.
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instructions},
                *st.session_state.messages[-10:]
            ],
            temperature=0.6
        )
        
        assistant_message = response.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(assistant_message)
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        memory.log_interaction(user_input, assistant_message)
        
        st.caption(f"⚡ {round(time.time() - start_time, 2)}s")
        
    except Exception as e:
        st.error(f"⚠️ Erreur : {e}")
    
    st.rerun()

# ================================================================
# SIDEBAR (Stats en direct)
# ================================================================

with st.sidebar:
    st.markdown("## 🧠 Statut Delta")
    try:
        e_count = memory.supabase.table("delta_entities").select("entity_id", count="exact").execute().count
        m_count = memory.supabase.table("delta_memories").select("id", count="exact").execute().count
        
        st.metric("Profils", e_count)
        st.metric("Souvenirs", m_count)
    except:
        st.warning("Base de données en attente...")
    
    if st.button("🧹 Vider la discussion"):
        st.session_state.messages = []
        st.rerun()
