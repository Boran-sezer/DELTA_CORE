# ================================================================
# DELTA OS - TRUE JARVIS COGNITIVE SYSTEM (INTEGRAL & CORRECTED)
# ================================================================

import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import time
import hashlib

# ================================================================
# CONFIGURATION
# ================================================================

st.set_page_config(
    page_title="JARVIS - Delta OS",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Style Tony Stark
st.markdown("""
<style>
    [data-testid='stSidebar'], header {display:none}
    body {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0f0f1e 100%);
        font-family: 'Courier New', monospace;
    }
    .main {background: transparent;}
    .stChatMessage {
        background: rgba(30, 144, 255, 0.05);
        border-left: 3px solid #1E90FF;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    h1 {
        color: #1E90FF;
        text-shadow: 0 0 10px #1E90FF;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# ================================================================
# JARVIS COGNITIVE ARCHITECTURE
# ================================================================

class JARVISCognitiveSystem:
    def __init__(self):
        self.supabase: Client = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )
        self.groq = Groq(api_key=st.secrets["groq"]["api_key"])
        self.owner = "boran"
        self._working_memory_cache = []
        self._semantic_cache = {}

    def update_working_memory(self, user_message: str, assistant_response: str):
        importance = self._calculate_importance(user_message)
        interaction = {
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.utcnow().isoformat(),
            "importance": importance
        }
        self._working_memory_cache.append(interaction)
        
        try:
            self.supabase.table("jarvis_working_memory").insert({
                "owner": self.owner,
                "user_message": user_message,
                "assistant_response": assistant_response,
                "timestamp": interaction['timestamp'],
                "importance": importance
            }).execute()
        except: pass

    def _calculate_importance(self, message: str) -> float:
        imp = 0.5
        keywords = ['important', 'projet', 'urgent', 'rappel', 'delta']
        if any(kw in message.lower() for kw in keywords): imp += 0.2
        if len(message) > 100: imp += 0.1
        return min(imp, 1.0)

    def store_semantic_fact(self, entity, fact_type, fact, confidence=0.9):
        entity_norm = entity.lower().strip()
        try:
            self.supabase.table("jarvis_semantic_memory").upsert({
                "owner": self.owner,
                "entity": entity_norm,
                "fact_type": fact_type,
                "fact": fact,
                "confidence": confidence,
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
            self._semantic_cache.setdefault(entity_norm, {})[fact_type] = fact
        except: pass

    def recall_semantic_facts(self, entity=None) -> Dict:
        entity_norm = entity.lower().strip() if entity else self.owner
        if entity_norm in self._semantic_cache: return self._semantic_cache[entity_norm]
        try:
            res = self.supabase.table("jarvis_semantic_memory").select("*").eq("owner", self.owner).eq("entity", entity_norm).execute()
            facts = {row['fact_type']: row['fact'] for row in res.data}
            self._semantic_cache[entity_norm] = facts
            return facts
        except: return {}

    def recall_recent_episodes(self, days=7) -> List[Dict]:
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        try:
            res = self.supabase.table("jarvis_episodic_memory").select("*").eq("owner", self.owner).gte("timestamp", cutoff).order("importance", desc=True).limit(5).execute()
            return res.data
        except: return []

    def learn_pattern(self, pattern_type, pattern_data):
        try:
            self.supabase.table("jarvis_procedural_memory").insert({
                "owner": self.owner, "pattern_type": pattern_type, "pattern_data": json.dumps(pattern_data), "strength": 0.5
            }).execute()
        except: pass

    def detect_patterns(self) -> List[Dict]:
        try:
            res = self.supabase.table("jarvis_procedural_memory").select("*").eq("owner", self.owner).gte("strength", 0.5).execute()
            return res.data
        except: return []

    def analyze_message(self, message: str) -> Dict:
        facts = self.recall_semantic_facts()
        prompt = f"Analyse ce message de {self.owner}: '{message}'. Contexte: {json.dumps(facts)}. Réponds en JSON strict avec semantic_facts, episodic_event, procedural_pattern, importance_score, anticipation."
        try:
            res = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Analyseur cognitif JSON."}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(res.choices[0].message.content)
        except: return {"semantic_facts": [], "importance_score": 0.5}

    def process_and_learn(self, message: str):
        analysis = self.analyze_message(message)
        
        # 1. Faits Sémantiques (Correction KeyError)
        facts = analysis.get('semantic_facts', [])
        for fact in facts:
            entity = fact.get("entity") or fact.get("entité") or "boran"
            f_type = fact.get("fact_type") or fact.get("type") or "info"
            f_val = fact.get("fact") or fact.get("valeur") or ""
            if f_val:
                self.store_semantic_fact(entity, f_type, f_val, fact.get("confidence", 0.9))
        
        # 2. Événement Épisodique
        ep = analysis.get('episodic_event', {})
        if ep.get('should_store'):
            try:
                self.supabase.table("jarvis_episodic_memory").insert({
                    "owner": self.owner, "event_type": ep.get('event_type', 'general'),
                    "description": ep.get('description', message[:100]), "importance": ep.get('importance', 0.7)
                }).execute()
            except: pass

        # 3. Patterns Procéduraux
        pat = analysis.get('procedural_pattern', {})
        if pat.get('detected'):
            self.learn_pattern(pat.get('pattern_type'), pat.get('pattern_data', {}))
            
        return analysis

    def get_full_context(self) -> str:
        parts = []
        facts = self.recall_semantic_facts()
        if facts: parts.append(f"PROFIL: {json.dumps(facts)}")
        episodes = self.recall_recent_episodes()
        if episodes: parts.append(f"ÉVÉNEMENTS: {[e['description'] for e in episodes]}")
        return "\n".join(parts)

# ================================================================
# INTERFACE & LOGIQUE DE CHAT
# ================================================================

if "jarvis" not in st.session_state:
    st.session_state.jarvis = JARVISCognitiveSystem()

jarvis = st.session_state.jarvis

st.markdown("# 🔷 J.A.R.V.I.S.")
st.caption("Architecture Cognitive Contextuelle v3.0")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Bonjour Monsieur Sezer. Tous les systèmes sont opérationnels."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if user_input := st.chat_input("Monsieur ?"):
    with st.chat_message("user"): st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # --- CYCLE COGNITIF ---
    with st.spinner("🧠 Cycle cognitif..."):
        learning_result = jarvis.process_and_learn(user_input)
        full_context = jarvis.get_full_context()

    # --- CAPTEURS CONTEXTUELS ---
    maintenant = datetime.now()
    date_context = maintenant.strftime("%A %d %B %Y")
    heure_context = maintenant.strftime("%H:%M")
    localisation_context = "Annecy, France"

    # --- GÉNÉRATION RÉPONSE ---
    system_instructions = f"""Tu es JARVIS, l'IA de Monsieur {jarvis.owner.upper()}.
    CONTEXTE RÉEL : Date: {date_context} | Heure: {heure_context} | Lieu: {localisation_context}
    MÉMOIRE : {full_context}
    ANTICIPATION : {learning_result.get('anticipation')}
    
    TON : Professionnel, sarcastique, proactif. Appelle-le 'Monsieur'. 
    Si Monsieur travaille tard ({heure_context}), sois ironique sur ses cycles de sommeil."""

    try:
        response = jarvis.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_instructions}] + st.session_state.messages[-10:],
            temperature=0.7
        )
        ans = response.choices[0].message.content
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        jarvis.update_working_memory(user_input, ans)
    except Exception as e:
        st.error(f"Erreur : {e}")
    
    st.rerun()

# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.markdown("## 🧠 Systèmes Mémoriels")
    memory_type = st.selectbox("Type", ["Sémantique", "Épisodique", "Travail"])
    if memory_type == "Sémantique":
        st.json(jarvis.recall_semantic_facts())
    elif memory_type == "Épisodique":
        st.write(jarvis.recall_recent_episodes())
    else:
        st.write(jarvis._working_memory_cache)
