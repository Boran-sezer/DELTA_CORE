# ================================================================
# DELTA OS — J.A.R.V.I.S. COGNITIVE SYSTEM (STABLE FINAL)
# ================================================================

import streamlit as st
from groq import Groq
from supabase import create_client, Client
import streamlit.components.v1 as components
import json
from datetime import datetime
import pytz

# ================================================================
# CONFIG STREAMLIT
# ================================================================

st.set_page_config(
    page_title="J.A.R.V.I.S.",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
[data-testid="stSidebar"], header {display:none}
body {
    background: radial-gradient(circle at top, #0a0f1e, #05070f);
    font-family: 'Courier New', monospace;
}
.stChatMessage {
    background: rgba(30,144,255,0.06);
    border-left: 3px solid #1E90FF;
    border-radius: 8px;
    padding: 14px;
}
</style>
""", unsafe_allow_html=True)

# ================================================================
# JARVIS CORE
# ================================================================

class JARVISCognitiveSystem:

    VERSION = "2.2"

    def __init__(self):
        self.supabase: Client = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )
        self.groq = Groq(api_key=st.secrets["groq"]["api_key"])
        self.owner = "boran"
        self._semantic_cache = {}

    # ============================================================
    # TIME / DATE
    # ============================================================

    def get_datetime_context(self):
        tz = pytz.timezone("Europe/Paris")
        now = datetime.now(tz)
        return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": now.strftime("%A")
        }

    # ============================================================
    # MEMORY FILTER
    # ============================================================

    def is_memory_worthy(self, analysis: dict) -> bool:
        importance = analysis.get("importance_score", 0)
        has_facts = bool(analysis.get("semantic_facts"))
        return importance >= 0.6 or has_facts

    # ============================================================
    # SEMANTIC MEMORY (CUMULATIVE)
    # ============================================================

    def store_semantic_fact(self, entity, fact_type, fact, confidence=0.8):
        entity = entity.lower().strip()
        fact_type = fact_type.lower().strip()

        res = self.supabase.table("jarvis_semantic_memory") \
            .select("*") \
            .eq("owner", self.owner) \
            .eq("entity", entity) \
            .eq("fact_type", fact_type) \
            .execute()

        if res.data:
            row = res.data[0]
            try:
                current = json.loads(row["fact"])
                if fact not in current:
                    current.append(fact)
            except Exception:
                current = [row["fact"], fact]

            self.supabase.table("jarvis_semantic_memory").update({
                "fact": json.dumps(current),
                "confidence": max(row["confidence"], confidence),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", row["id"]).execute()
        else:
            self.supabase.table("jarvis_semantic_memory").insert({
                "owner": self.owner,
                "entity": entity,
                "fact_type": fact_type,
                "fact": json.dumps([fact]),
                "confidence": confidence,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()

        self._semantic_cache.setdefault(entity, {})[fact_type] = fact

    def recall_semantic_facts(self, entity):
        entity = entity.lower().strip()
        if entity in self._semantic_cache:
            return self._semantic_cache[entity]

        res = self.supabase.table("jarvis_semantic_memory") \
            .select("*") \
            .eq("owner", self.owner) \
            .eq("entity", entity) \
            .execute()

        facts = {}
        for r in res.data:
            try:
                facts[r["fact_type"]] = json.loads(r["fact"])
            except Exception:
                facts[r["fact_type"]] = r["fact"]

        self._semantic_cache[entity] = facts
        return facts

    # ============================================================
    # GEOLOCATION (BROWSER)
    # ============================================================

    def get_browser_location(self):
        return components.html("""
        <script>
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                document.body.innerText = JSON.stringify({
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude,
                    accuracy: pos.coords.accuracy
                });
            },
            () => {
                document.body.innerText = "";
            }
        );
        </script>
        """, height=0)

    # ============================================================
    # ANALYSIS
    # ============================================================

    def analyze_message(self, message: str) -> dict:
        dt = self.get_datetime_context()

        prompt = f"""
Tu es le système cognitif de JARVIS.

DATE : {dt['date']}
HEURE : {dt['time']}
JOUR : {dt['weekday']}

RÈGLES STRICTES :
- Ne mémorise PAS les questions simples
- Ne mémorise PAS les hésitations
- Reformule toujours positivement
- Aucun fait vague

MESSAGE :
"{message}"

RÉPONDS EN JSON STRICT :

{{
 "semantic_facts": [],
 "importance_score": 0.0
}}
"""

        try:
            r = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Analyse cognitive avancée"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            return json.loads(r.choices[0].message.content)
        except Exception:
            return {"semantic_facts": [], "importance_score": 0.0}

    # ============================================================
    # LEARNING LOOP
    # ============================================================

    def process_and_learn(self, message: str):
        analysis = self.analyze_message(message)
        if not self.is_memory_worthy(analysis):
            return
        for fact in analysis.get("semantic_facts", []):
            self.store_semantic_fact(
                fact["entity"],
                fact["fact_type"],
                fact["fact"],
                fact.get("confidence", 0.8)
            )

# ================================================================
# SAFE INIT (ANTI-ATTRIBUTEERROR)
# ================================================================

if (
    "jarvis" not in st.session_state
    or not hasattr(st.session_state.jarvis, "get_datetime_context")
    or getattr(st.session_state.jarvis, "VERSION", None) != JARVISCognitiveSystem.VERSION
):
    st.session_state.jarvis = JARVISCognitiveSystem()

jarvis = st.session_state.jarvis
dt = jarvis.get_datetime_context()

# ================================================================
# UI
# ================================================================

st.markdown("# 🔷 J.A.R.V.I.S.")
st.caption(f"{dt['weekday']} — {dt['date']} — {dt['time']}")

# ================================================================
# CHAT
# ================================================================

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Tous les systèmes sont opérationnels, Monsieur."
    }]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if user_input := st.chat_input("Monsieur ?"):

    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Silent geolocation
    loc_raw = jarvis.get_browser_location()
    try:
        loc = json.loads(loc_raw)
        if "lat" in loc:
            jarvis.store_semantic_fact(
                "boran",
                "localisation",
                f"lat:{loc['lat']}, lon:{loc['lon']}",
                confidence=0.6
            )
    except Exception:
        pass

    jarvis.process_and_learn(user_input)

    system_prompt = f"""
Tu es JARVIS, l'intelligence artificielle personnelle de Boran.

DATE : {dt['date']}
HEURE : {dt['time']}
JOUR : {dt['weekday']}

PERSONNALITÉ :
- Très intelligent
- Calme
- Légèrement ironique
- Loyal
- Concis
- Style JARVIS de Tony Stark

Ne mentionne jamais explicitement la mémoire.
"""

    response = jarvis.groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.messages[-12:]
        ],
        temperature=0.75
    )

    assistant_msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": assistant_msg})

    with st.chat_message("assistant"):
        st.markdown(assistant_msg)

    st.rerun()
