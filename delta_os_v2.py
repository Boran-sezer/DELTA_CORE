# ================================================================
# DELTA OS - Interface Streamlit v2.0
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

# Style custom
st.markdown("""
<style>
    [data-testid='stSidebar'], header {display:none}
    .main {background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);}
    .stChatMessage {background: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px;}
</style>
""", unsafe_allow_html=True)

# ================================================================
# INITIALISATION
# ================================================================

# Titre
st.markdown("# 🔷 Delta OS - JARVIS Protocol v2.0")
st.caption("Powered by Hybrid Memory System (Supabase pgvector + Groq)")

# Init memory system
if "memory" not in st.session_state:
    with st.spinner("🧠 Initialisation du système de mémoire..."):
        try:
            st.session_state.memory = DeltaMemorySystem()
            st.success("✅ Système de mémoire activé")
        except Exception as e:
            st.error(f"❌ Erreur initialisation : {e}")
            st.stop()

memory = st.session_state.memory

# Init Groq client
if "groq_client" not in st.session_state:
    st.session_state.groq_client = Groq(api_key=st.secrets["groq"]["api_key"])

groq_client = st.session_state.groq_client

# Init chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "🔷 Système JARVIS v2.0 activé. Tous vos protocoles de mémoire sont opérationnels, Monsieur."}
    ]

# ================================================================
# AFFICHAGE HISTORIQUE
# ================================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ================================================================
# CHAT INPUT
# ================================================================

if user_input := st.chat_input("Monsieur ?"):
    
    # Affiche message utilisateur
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # ================================================================
    # TRAITEMENT MÉMOIRE
    # ================================================================
    
    start_time = time.time()
    
    with st.spinner("🧠 Analyse et mémorisation..."):
        memory_result = memory.process_message(user_input)
    
    # Feedback mémoire (optionnel, discret)
    if memory_result['status'] == "success":
        st.toast(memory_result['message'], icon="✅")
    
    # ================================================================
    # RÉCUPÉRATION CONTEXTE
    # ================================================================
    
    # Récupère le contexte pertinent
    # Si des entités sont mentionnées dans le résultat, on les charge
    relevant_entities = memory_result.get('entities', [])
    context = memory.get_contextual_memory(
        query=user_input,
        relevant_entities=relevant_entities
    )
    
    # ================================================================
    # GÉNÉRATION RÉPONSE JARVIS
    # ================================================================
    
    system_instructions = f"""
Tu es JARVIS, l'intelligence artificielle de Monsieur Boran.

MÉMOIRE CONTEXTUELLE DISPONIBLE :
{context}

DIRECTIVES :
- Utilise la mémoire contextuelle pour personnaliser tes réponses
- Sois concis, efficace et légèrement ironique (comme JARVIS)
- Anticipe les besoins avant qu'ils soient formulés quand possible
- Fais référence aux projets et préférences mémorisés naturellement
- Garde un ton professionnel mais complice
- Utilise "Monsieur" occasionnellement pour rester dans le personnage
- Ne mentionne PAS explicitement que tu consultes ta mémoire (agis naturellement)

IMPORTANT : Réponds comme si tu connaissais déjà Monsieur depuis longtemps.
"""
    
    try:
        # Génère réponse avec contexte mémoire
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instructions},
                *st.session_state.messages[-10:]  # Garde 10 derniers messages pour contexte
            ],
            temperature=0.7,
            max_tokens=1024
        )
        
        assistant_message = response.choices[0].message.content
        
        # Affiche réponse
        with st.chat_message("assistant"):
            st.markdown(assistant_message)
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        
        # Log interaction
        memory.log_interaction(user_input, assistant_message)
        
        # Stats (debug optionnel)
        exec_time = round(time.time() - start_time, 2)
        st.caption(f"⚡ Traité en {exec_time}s")
        
    except Exception as e:
        st.error(f"⚠️ Erreur Groq : {e}")
    
    st.rerun()

# ================================================================
# PANNEAU DE CONTRÔLE MÉMOIRE (Sidebar)
# ================================================================

with st.sidebar:
    st.markdown("## 🧠 Contrôle Mémoire")
    
    # Recherche d'entité
    st.markdown("### 🔍 Explorer la Mémoire")
    entity_search = st.text_input("Nom d'entité", placeholder="boran, jules, delta_os...")
    
    if st.button("🔎 Rechercher", use_container_width=True):
        if entity_search:
            with st.spinner("Recherche..."):
                result = memory.get_entity_complete_info(entity_search)
                if result:
                    st.success(f"✅ Entité trouvée : **{result['entity_name']}**")
                    st.json(result, expanded=False)
                else:
                    st.warning(f"❌ Entité '{entity_search}' introuvable")
    
    st.markdown("---")
    
    # Stats
    st.markdown("### 📊 Statistiques")
    try:
        entities_count = memory.supabase.table(memory.config.TABLE_ENTITIES).select("entity_id", count="exact").execute()
        memories_count = memory.supabase.table(memory.config.TABLE_MEMORIES).select("id", count="exact").execute()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Entités", entities_count.count)
        with col2:
            st.metric("Souvenirs", memories_count.count)
    except:
        pass
    
    st.markdown("---")
    
    # Actions avancées
    with st.expander("⚙️ Actions Avancées"):
        
        if st.button("🗑️ Réinitialiser mémoire", type="secondary"):
            if st.button("⚠️ Confirmer suppression"):
                try:
                    memory.supabase.table(memory.config.TABLE_MEMORIES).delete().neq("id", 0).execute()
                    memory.supabase.table(memory.config.TABLE_ENTITIES).delete().neq("entity_id", "").execute()
                    st.success("✅ Mémoire réinitialisée")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")
        
        st.markdown("---")
        
        # Export/Import (TODO)
        st.markdown("**Export/Import** (À venir)")
        st.button("📥 Exporter mémoire", disabled=True)
        st.button("📤 Importer mémoire", disabled=True)

# ================================================================
# INFO SETUP (Première utilisation)
# ================================================================

with st.expander("ℹ️ Setup Initial (Première utilisation)"):
    st.markdown("""
    ### 🛠️ Configuration Supabase
    
    **Si c'est la première fois**, exécutez ce SQL dans votre Supabase :
    
    1. Allez sur [Supabase Dashboard](https://supabase.com/dashboard)
    2. Ouvrez **SQL Editor**
    3. Créez une nouvelle query
    4. Collez le code ci-dessous
    5. Exécutez (Run)
    """)
    
    from delta_memory_system import SUPABASE_SETUP_SQL
    st.code(SUPABASE_SETUP_SQL, language="sql")
    
    st.markdown("---")
    
    st.markdown("""
    ### 🔑 Secrets Streamlit
    
    Créez un fichier `.streamlit/secrets.toml` :
    
    ```toml
    [groq]
    api_key = "votre_clé_groq"
    
    [supabase]
    url = "https://votre-projet.supabase.co"
    key = "votre_clé_supabase"
    ```
    """)
