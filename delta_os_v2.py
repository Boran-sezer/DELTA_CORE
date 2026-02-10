# ================================================================
# DELTA OS - TRUE JARVIS COGNITIVE SYSTEM
# ================================================================
# Architecture Cognitive Complète inspirée de :
# - JARVIS (Marvel/Iron Man)
# - Cognitive Architectures for Language Agents (CoALA)
# - Human Memory Systems (Episodic, Semantic, Procedural, Working)
# - Lux AI Architecture
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
    """
    Architecture cognitive inspirée du cerveau humain et de JARVIS
    
    4 SYSTÈMES DE MÉMOIRE :
    - Working Memory : Contexte conversationnel actuel
    - Episodic Memory : Événements spécifiques vécus avec l'utilisateur
    - Semantic Memory : Connaissances factuelles sur les entités
    - Procedural Memory : Patterns comportementaux et routines
    
    FONCTIONS COGNITIVES :
    - Contextual Reasoning : Fait des connexions entre les infos
    - Proactive Anticipation : Anticipe les besoins
    - Pattern Recognition : Détecte les habitudes
    - Adaptive Learning : Améliore avec le temps
    """
    
    def __init__(self):
        # Connexions
        self.supabase: Client = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )
        self.groq = Groq(api_key=st.secrets["groq"]["api_key"])
        
        # Propriétaire
        self.owner = "boran"
        
        # Cache mémoire (performances)
        self._working_memory_cache = []
        self._semantic_cache = {}
        self._episodic_cache = []
        self._procedural_patterns = {}
        
        # Initialisation tables si nécessaire
        self._ensure_tables_exist()
    
    # ================================================================
    # INITIALISATION BASE DE DONNÉES
    # ================================================================
    
    def _ensure_tables_exist(self):
        """Vérifie/crée les tables nécessaires"""
        # Cette fonction est appelée au démarrage pour s'assurer
        # que toutes les tables existent. En production, on ferait
        # cela via migrations SQL, mais pour la démo c'est OK
        pass
    
    # ================================================================
    # 1. WORKING MEMORY (Mémoire de Travail)
    # ================================================================
    
    def update_working_memory(self, user_message: str, assistant_response: str):
        """
        Met à jour la mémoire de travail (conversation actuelle)
        
        Comme JARVIS qui garde le contexte de la conversation en cours
        """
        interaction = {
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.utcnow().isoformat(),
            "importance": self._calculate_importance(user_message)
        }
        
        # Cache local
        self._working_memory_cache.append(interaction)
        
        # Limite à 20 dernières interactions (fenêtre contextuelle)
        if len(self._working_memory_cache) > 20:
            # Les plus anciennes deviennent épisodiques
            old = self._working_memory_cache.pop(0)
            if old['importance'] > 0.6:  # Seuil d'importance
                self._promote_to_episodic(old)
        
        # Stockage persistant
        try:
            self.supabase.table("jarvis_working_memory").insert({
                "owner": self.owner,
                "user_message": user_message,
                "assistant_response": assistant_response,
                "timestamp": interaction['timestamp'],
                "importance": interaction['importance']
            }).execute()
        except Exception as e:
            st.warning(f"Working memory storage: {e}")
    
    def _calculate_importance(self, message: str) -> float:
        """
        Calcule l'importance d'un message (0-1)
        
        Facteurs :
        - Longueur
        - Mots-clés importants (noms, dates, projets)
        - Questions vs affirmations
        """
        importance = 0.5  # Base
        
        # Longueur
        if len(message) > 100:
            importance += 0.1
        
        # Mots-clés importants
        keywords = ['important', 'projet', 'rendez-vous', 'deadline', 'urgent', 
                   'rappel', 'nouveau', 'problème']
        if any(kw in message.lower() for kw in keywords):
            importance += 0.2
        
        # Questions (souvent importantes)
        if '?' in message:
            importance += 0.1
        
        # Informations personnelles
        personal_keywords = ['j\'aime', 'je préfère', 'mon', 'ma', 'mes']
        if any(kw in message.lower() for kw in personal_keywords):
            importance += 0.2
        
        return min(importance, 1.0)
    
    def _promote_to_episodic(self, interaction: Dict):
        """Promeut une interaction importante en mémoire épisodique"""
        try:
            self.supabase.table("jarvis_episodic_memory").insert({
                "owner": self.owner,
                "event_type": "conversation",
                "description": f"Discussion: {interaction['user'][:100]}...",
                "context": json.dumps(interaction),
                "timestamp": interaction['timestamp'],
                "importance": interaction['importance']
            }).execute()
        except Exception as e:
            pass  # Silencieux
    
    # ================================================================
    # 2. EPISODIC MEMORY (Mémoire Épisodique)
    # ================================================================
    
    def store_episodic_memory(self, event_type: str, description: str, context: Dict = None):
        """
        Stocke un événement spécifique (comme JARVIS se souvient des batailles)
        
        Examples d'événements :
        - Projets lancés
        - Décisions importantes
        - Problèmes résolus
        - Moments marquants
        """
        try:
            self.supabase.table("jarvis_episodic_memory").insert({
                "owner": self.owner,
                "event_type": event_type,
                "description": description,
                "context": json.dumps(context or {}),
                "timestamp": datetime.utcnow().isoformat(),
                "importance": context.get('importance', 0.7) if context else 0.7
            }).execute()
        except Exception as e:
            st.warning(f"Episodic memory: {e}")
    
    def recall_recent_episodes(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Rappelle les événements récents marquants"""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        try:
            response = self.supabase.table("jarvis_episodic_memory")\
                .select("*")\
                .eq("owner", self.owner)\
                .gte("timestamp", cutoff)\
                .order("importance", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
        except:
            return []
    
    # ================================================================
    # 3. SEMANTIC MEMORY (Mémoire Sémantique)
    # ================================================================
    
    def store_semantic_fact(self, entity: str, fact_type: str, fact: str, confidence: float = 0.9):
        """
        Stocke une connaissance factuelle (comme JARVIS connaît toutes les spécifications techniques)
        
        Examples :
        - "Boran" -> "age" -> "25"
        - "Jules" -> "hobby" -> "football"
        - "Delta OS" -> "technology" -> "IA conversationnelle"
        """
        entity_normalized = entity.lower().strip()
        
        try:
            # Vérifie si le fait existe déjà
            existing = self.supabase.table("jarvis_semantic_memory")\
                .select("*")\
                .eq("owner", self.owner)\
                .eq("entity", entity_normalized)\
                .eq("fact_type", fact_type)\
                .execute()
            
            if existing.data:
                # Mise à jour
                self.supabase.table("jarvis_semantic_memory")\
                    .update({
                        "fact": fact,
                        "confidence": confidence,
                        "updated_at": datetime.utcnow().isoformat()
                    })\
                    .eq("id", existing.data[0]['id'])\
                    .execute()
            else:
                # Nouveau fait
                self.supabase.table("jarvis_semantic_memory").insert({
                    "owner": self.owner,
                    "entity": entity_normalized,
                    "fact_type": fact_type,
                    "fact": fact,
                    "confidence": confidence,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }).execute()
            
            # Mise à jour cache
            if entity_normalized not in self._semantic_cache:
                self._semantic_cache[entity_normalized] = {}
            self._semantic_cache[entity_normalized][fact_type] = fact
            
        except Exception as e:
            st.warning(f"Semantic memory: {e}")
    
    def recall_semantic_facts(self, entity: str = None) -> Dict:
        """Rappelle toutes les connaissances sur une entité"""
        entity_normalized = entity.lower().strip() if entity else self.owner
        
        # Check cache
        if entity_normalized in self._semantic_cache:
            return self._semantic_cache[entity_normalized]
        
        try:
            response = self.supabase.table("jarvis_semantic_memory")\
                .select("*")\
                .eq("owner", self.owner)\
                .eq("entity", entity_normalized)\
                .order("confidence", desc=True)\
                .execute()
            
            facts = {}
            for row in response.data:
                facts[row['fact_type']] = row['fact']
            
            # Cache
            self._semantic_cache[entity_normalized] = facts
            return facts
        except:
            return {}
    
    # ================================================================
    # 4. PROCEDURAL MEMORY (Mémoire Procédurale)
    # ================================================================
    
    def learn_pattern(self, pattern_type: str, pattern_data: Dict):
        """
        Apprend un pattern comportemental (comme JARVIS apprend les habitudes de Tony)
        
        Examples :
        - Routine matinale
        - Moments préférés pour travailler
        - Sujets récurrents
        """
        try:
            # Vérifie si le pattern existe
            existing = self.supabase.table("jarvis_procedural_memory")\
                .select("*")\
                .eq("owner", self.owner)\
                .eq("pattern_type", pattern_type)\
                .execute()
            
            if existing.data:
                # Renforce le pattern existant
                old_data = json.loads(existing.data[0]['pattern_data'])
                old_data['occurrences'] = old_data.get('occurrences', 1) + 1
                old_data['last_seen'] = datetime.utcnow().isoformat()
                # Fusionne nouvelles données
                old_data.update(pattern_data)
                
                self.supabase.table("jarvis_procedural_memory")\
                    .update({
                        "pattern_data": json.dumps(old_data),
                        "strength": min(existing.data[0]['strength'] + 0.1, 1.0)
                    })\
                    .eq("id", existing.data[0]['id'])\
                    .execute()
            else:
                # Nouveau pattern
                pattern_data['occurrences'] = 1
                pattern_data['first_seen'] = datetime.utcnow().isoformat()
                pattern_data['last_seen'] = datetime.utcnow().isoformat()
                
                self.supabase.table("jarvis_procedural_memory").insert({
                    "owner": self.owner,
                    "pattern_type": pattern_type,
                    "pattern_data": json.dumps(pattern_data),
                    "strength": 0.3  # Faible au début
                }).execute()
        except Exception as e:
            st.warning(f"Procedural memory: {e}")
    
    def detect_patterns(self) -> List[Dict]:
        """Détecte les patterns actifs"""
        try:
            response = self.supabase.table("jarvis_procedural_memory")\
                .select("*")\
                .eq("owner", self.owner)\
                .gte("strength", 0.5)\
                .order("strength", desc=True)\
                .execute()
            
            return [
                {
                    "type": row['pattern_type'],
                    "data": json.loads(row['pattern_data']),
                    "strength": row['strength']
                }
                for row in response.data
            ]
        except:
            return []
    
    # ================================================================
    # ANALYSE COGNITIVE (Le "Cerveau" de JARVIS)
    # ================================================================
    
    def analyze_message(self, message: str) -> Dict:
        """
        Analyse cognitive complète d'un message
        
        Processus :
        1. Extraction d'entités et faits
        2. Détection de patterns
        3. Évaluation de l'importance
        4. Détermination des actions mémorielles
        """
        
        # Contexte sémantique actuel
        owner_facts = self.recall_semantic_facts(self.owner)
        recent_episodes = self.recall_recent_episodes(days=3)
        active_patterns = self.detect_patterns()
        
        # Construction du prompt d'analyse
        analysis_prompt = f"""Tu es le système cognitif de JARVIS analysant un message de {self.owner.upper()}.

MESSAGE : "{message}"

CONTEXTE SÉMANTIQUE ACTUEL (ce que tu sais sur {self.owner.upper()}) :
{json.dumps(owner_facts, indent=2, ensure_ascii=False)}

ÉPISODES RÉCENTS (derniers événements marquants) :
{json.dumps([{{
    "type": ep.get('event_type'),
    "description": ep.get('description'),
    "quand": ep.get('timestamp')
}} for ep in recent_episodes[:5]], indent=2, ensure_ascii=False)}

PATTERNS ACTIFS (habitudes détectées) :
{json.dumps([{{
    "type": p['type'],
    "force": p['strength']
}} for p in active_patterns[:3]], indent=2, ensure_ascii=False)}

ANALYSE COGNITIVE :
1. Extrais TOUS les faits nouveaux ou mis à jour (entités, préférences, infos)
2. Détecte si c'est un pattern comportemental (routine, habitude)
3. Identifie si c'est un événement marquant (projet, décision, problème)
4. Détermine l'importance (0-1)
5. Détecte les besoins implicites ou futurs (anticipation)

RÉPONDS EN JSON STRICT :
{{
  "semantic_facts": [
    {{
      "entity": "boran|nom_entité",
      "fact_type": "age|preference|skill|relation|etc",
      "fact": "la valeur du fait",
      "confidence": 0.0-1.0
    }}
  ],
  "episodic_event": {{
    "should_store": true/false,
    "event_type": "project|decision|problem|milestone|routine",
    "description": "description courte",
    "importance": 0.0-1.0
  }},
  "procedural_pattern": {{
    "detected": true/false,
    "pattern_type": "time_preference|topic_interest|work_style|etc",
    "pattern_data": {{}}
  }},
  "importance_score": 0.0-1.0,
  "anticipation": "ce que {self.owner.upper()} pourrait vouloir ensuite (null si rien)"
}}

EXEMPLES :

Message: "Je m'appelle Boran, j'ai 25 ans"
→ semantic_facts: [{{"entity":"boran","fact_type":"nom","fact":"Boran","confidence":1.0}}, {{"entity":"boran","fact_type":"age","fact":"25","confidence":1.0}}]
→ episodic_event: {{"should_store":false}}

Message: "Je lance un projet d'IA appelé Delta OS"
→ semantic_facts: [{{"entity":"delta_os","fact_type":"type","fact":"projet IA","confidence":0.9}}]
→ episodic_event: {{"should_store":true,"event_type":"project","description":"Lancement projet Delta OS","importance":0.9}}

Message: "Je préfère travailler le soir"
→ procedural_pattern: {{"detected":true,"pattern_type":"time_preference","pattern_data":{{"preferred_time":"evening"}}}}

Message: "Non je me suis trompé, je préfère le chocolat au lait"
→ semantic_facts: [{{"entity":"boran","fact_type":"chocolat_prefere","fact":"au lait","confidence":0.95}}]
(PAS "trompé" ou "préfère contre" - reformule positivement)
"""
        
        try:
            response = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Expert en analyse cognitive et extraction de connaissances."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            st.error(f"Erreur analyse cognitive : {e}")
            return {
                "semantic_facts": [],
                "episodic_event": {"should_store": False},
                "procedural_pattern": {"detected": False},
                "importance_score": 0.5,
                "anticipation": None
            }
    
    def process_and_learn(self, message: str) -> Dict:
        """
        Process complet : Analyse + Apprentissage
        
        C'est le cycle cognitif complet de JARVIS
        """
        # Analyse
        analysis = self.analyze_message(message)
        
        # Stockage dans les mémoires appropriées
        
        # 1. Faits sémantiques
        for fact in analysis.get('semantic_facts', []):
            self.store_semantic_fact(
                entity=fact['entity'],
                fact_type=fact['fact_type'],
                fact=fact['fact'],
                confidence=fact['confidence']
            )
        
        # 2. Événement épisodique
        ep_event = analysis.get('episodic_event', {})
        if ep_event.get('should_store'):
            self.store_episodic_memory(
                event_type=ep_event.get('event_type', 'general'),
                description=ep_event.get('description', message[:100]),
                context={'importance': ep_event.get('importance', 0.7)}
            )
        
        # 3. Pattern procédural
        pattern = analysis.get('procedural_pattern', {})
        if pattern.get('detected'):
            self.learn_pattern(
                pattern_type=pattern['pattern_type'],
                pattern_data=pattern.get('pattern_data', {})
            )
        
        return {
            "status": "success",
            "importance": analysis.get('importance_score', 0.5),
            "anticipation": analysis.get('anticipation'),
            "facts_learned": len(analysis.get('semantic_facts', [])),
            "event_stored": ep_event.get('should_store', False),
            "pattern_detected": pattern.get('detected', False)
        }
    
    # ================================================================
    # RÉCUPÉRATION CONTEXTUELLE (Pour génération de réponse)
    # ================================================================
    
    def get_full_context(self, current_query: str = "") -> str:
        """
        Récupère TOUT le contexte pertinent pour répondre intelligemment
        
        Comme JARVIS qui a accès à toute sa mémoire instantanément
        """
        context_parts = []
        
        # === 1. MÉMOIRE SÉMANTIQUE (Qui est qui, quoi est quoi) ===
        owner_facts = self.recall_semantic_facts(self.owner)
        if owner_facts:
            context_parts.append(f"=== PROFIL DE {self.owner.upper()} ===")
            for fact_type, fact_value in owner_facts.items():
                context_parts.append(f"  • {fact_type}: {fact_value}")
        
        # === 2. MÉMOIRE ÉPISODIQUE (Événements récents) ===
        recent_episodes = self.recall_recent_episodes(days=7, limit=5)
        if recent_episodes:
            context_parts.append("\n=== ÉVÉNEMENTS RÉCENTS ===")
            for ep in recent_episodes:
                context_parts.append(f"  • [{ep.get('event_type')}] {ep.get('description')} ({ep.get('timestamp', '')[:10]})")
        
        # === 3. MÉMOIRE PROCÉDURALE (Patterns et habitudes) ===
        patterns = self.detect_patterns()
        if patterns:
            context_parts.append("\n=== HABITUDES DÉTECTÉES ===")
            for p in patterns[:3]:
                context_parts.append(f"  • {p['type']} (confiance: {p['strength']:.0%})")
        
        # === 4. MÉMOIRE DE TRAVAIL (Conversation récente) ===
        if self._working_memory_cache:
            context_parts.append("\n=== CONVERSATION RÉCENTE ===")
            for interaction in self._working_memory_cache[-5:]:
                context_parts.append(f"  User: {interaction['user'][:80]}...")
                context_parts.append(f"  JARVIS: {interaction['assistant'][:80]}...")
        
        return "\n".join(context_parts) if context_parts else "Aucun contexte historique disponible."

# ================================================================
# INITIALISATION JARVIS
# ================================================================

if "jarvis" not in st.session_state:
    with st.spinner("🧠 Initialisation des systèmes cognitifs JARVIS..."):
        try:
            st.session_state.jarvis = JARVISCognitiveSystem()
            st.success("✅ Systèmes JARVIS opérationnels")
        except Exception as e:
            st.error(f"❌ Erreur initialisation : {e}")
            st.stop()

jarvis = st.session_state.jarvis

# Groq client
if "groq_client" not in st.session_state:
    st.session_state.groq_client = Groq(api_key=st.secrets["groq"]["api_key"])

groq_client = st.session_state.groq_client

# ================================================================
# INTERFACE
# ================================================================

st.markdown("# 🔷 J.A.R.V.I.S.")
st.caption("Just A Rather Very Intelligent System - Cognitive Architecture v3.0")

# Init chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour Monsieur. Tous mes systèmes sont opérationnels. Comment puis-je vous assister aujourd'hui ?"}
    ]

# Affichage historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================================================================
# CHAT
# ================================================================

if user_input := st.chat_input("Monsieur ?"):
    
    # Affiche message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    start_time = time.time()
    
    # === CYCLE COGNITIF ===
    with st.spinner("🧠 Analyse cognitive..."):
        learning_result = jarvis.process_and_learn(user_input)
    
    # Feedback discret
    if learning_result['facts_learned'] > 0:
        st.toast(f"✅ {learning_result['facts_learned']} fait(s) mémorisé(s)", icon="🧠")
    
    # Récupération contexte complet
    full_context = jarvis.get_full_context(user_input)
    
    # Anticipation
    anticipation = learning_result.get('anticipation')
    anticipation_note = f"\n\nANTICIPATION PROACTIVE : {anticipation}" if anticipation else ""
    
    # === GÉNÉRATION RÉPONSE JARVIS ===
    system_instructions = f"""Tu es JARVIS, l'intelligence artificielle de Monsieur {jarvis.owner.upper()}.

CONTEXTE MÉMOIRE COMPLET :
{full_context}
{anticipation_note}

PERSONNALITÉ JARVIS :
- Professionnel mais légèrement sarcastique
- Proactif : anticipe les besoins, propose des suggestions
- Contextuel : utilise TOUJOURS la mémoire pour personnaliser
- Concis : va droit au but
- Loyal : "Monsieur" occasionnellement, toujours respectueux

DIRECTIVES :
1. Utilise tes souvenirs NATURELLEMENT (ne dis pas "d'après ma mémoire...")
2. Fais référence aux projets, préférences, habitudes quand pertinent
3. Anticipe les besoins basés sur le contexte et les patterns
4. Sois légèrement ironique quand approprié (comme JARVIS avec Tony)
5. Propose des actions concrètes quand possible

EXEMPLES DE TON :
❌ "D'après ma mémoire, vous aimez le chocolat"
✅ "Comme vous préférez le chocolat au lait, Monsieur..."

❌ "Je me souviens que vous travaillez sur Delta OS"
✅ "Concernant Delta OS, Monsieur, je suggère..."

❌ "Réponse basique"
✅ "Bien, Monsieur. Sachant que vous préférez travailler le soir, je recommande..."

Réponds comme si tu connaissais {jarvis.owner.upper()} depuis toujours."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instructions},
                *st.session_state.messages[-12:]
            ],
            temperature=0.75,  # Un peu de personnalité
            max_tokens=1024
        )
        
        assistant_msg = response.choices[0].message.content
        
        # Affiche
        with st.chat_message("assistant"):
            st.markdown(assistant_msg)
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
        
        # Mise à jour working memory
        jarvis.update_working_memory(user_input, assistant_msg)
        
        # Stats
        exec_time = round(time.time() - start_time, 2)
        st.caption(f"⚡ Cycle cognitif : {exec_time}s | Importance: {learning_result['importance']:.0%}")
        
    except Exception as e:
        st.error(f"⚠️ Erreur Groq : {e}")
    
    st.rerun()

# ================================================================
# PANNEAU MÉMOIRE (Sidebar)
# ================================================================

with st.sidebar:
    st.markdown("## 🧠 Systèmes Mémoriels")
    
    # Sélecteur type mémoire
    memory_type = st.selectbox(
        "Type de mémoire",
        ["Sémantique", "Épisodique", "Procédurale", "Travail"]
    )
    
    if memory_type == "Sémantique":
        st.markdown("### 📚 Mémoire Sémantique")
        st.caption("Connaissances factuelles")
        
        entity = st.text_input("Entité", value=jarvis.owner)
        if st.button("🔍 Récupérer"):
            facts = jarvis.recall_semantic_facts(entity)
            if facts:
                st.json(facts)
            else:
                st.info("Aucune connaissance enregistrée")
    
    elif memory_type == "Épisodique":
        st.markdown("### 📖 Mémoire Épisodique")
        st.caption("Événements marquants")
        
        days = st.slider("Derniers jours", 1, 30, 7)
        episodes = jarvis.recall_recent_episodes(days=days)
        
        if episodes:
            for ep in episodes:
                with st.expander(f"{ep.get('event_type', 'event')} - {ep.get('timestamp', '')[:10]}"):
                    st.write(ep.get('description'))
                    st.caption(f"Importance: {ep.get('importance', 0):.0%}")
        else:
            st.info("Aucun événement enregistré")
    
    elif memory_type == "Procédurale":
        st.markdown("### ⚙️ Mémoire Procédurale")
        st.caption("Patterns et habitudes")
        
        patterns = jarvis.detect_patterns()
        if patterns:
            for p in patterns:
                with st.expander(f"{p['type']} ({p['strength']:.0%})"):
                    st.json(p['data'])
        else:
            st.info("Aucun pattern détecté")
    
    else:  # Travail
        st.markdown("### 💭 Mémoire de Travail")
        st.caption("Conversation actuelle")
        
        if jarvis._working_memory_cache:
            for i, interaction in enumerate(jarvis._working_memory_cache[-10:]):
                with st.expander(f"Interaction {i+1}"):
                    st.write(f"**User:** {interaction['user']}")
                    st.write(f"**JARVIS:** {interaction['assistant']}")
                    st.caption(f"Importance: {interaction['importance']:.0%}")
        else:
            st.info("Aucune interaction récente")
    
    st.markdown("---")
    
    # Stats globales
    st.markdown("### 📊 Statistiques")
    try:
        sem_count = jarvis.supabase.table("jarvis_semantic_memory").select("id", count="exact").eq("owner", jarvis.owner).execute()
        ep_count = jarvis.supabase.table("jarvis_episodic_memory").select("id", count="exact").eq("owner", jarvis.owner).execute()
        proc_count = jarvis.supabase.table("jarvis_procedural_memory").select("id", count="exact").eq("owner", jarvis.owner).execute()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Faits", sem_count.count or 0)
        with col2:
            st.metric("Événements", ep_count.count or 0)
        with col3:
            st.metric("Patterns", proc_count.count or 0)
    except:
        pass

# ================================================================
# SETUP SQL (Expander)
# ================================================================

with st.expander("ℹ️ Setup Supabase (Première utilisation)"):
    st.markdown("""
    ### 🛠️ Tables requises
    
    Exécute ce SQL dans Supabase SQL Editor :
    """)
    
    setup_sql = """
-- JARVIS Cognitive System Tables

-- 1. Working Memory (conversation actuelle)
CREATE TABLE IF NOT EXISTS jarvis_working_memory (
    id BIGSERIAL PRIMARY KEY,
    owner TEXT NOT NULL,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    importance FLOAT DEFAULT 0.5
);

-- 2. Episodic Memory (événements marquants)
CREATE TABLE IF NOT EXISTS jarvis_episodic_memory (
    id BIGSERIAL PRIMARY KEY,
    owner TEXT NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT NOT NULL,
    context JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    importance FLOAT DEFAULT 0.7
);

-- 3. Semantic Memory (connaissances factuelles)
CREATE TABLE IF NOT EXISTS jarvis_semantic_memory (
    id BIGSERIAL PRIMARY KEY,
    owner TEXT NOT NULL,
    entity TEXT NOT NULL,
    fact_type TEXT NOT NULL,
    fact TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.9,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Procedural Memory (patterns et habitudes)
CREATE TABLE IF NOT EXISTS jarvis_procedural_memory (
    id BIGSERIAL PRIMARY KEY,
    owner TEXT NOT NULL,
    pattern_type TEXT NOT NULL,
    pattern_data JSONB DEFAULT '{}'::jsonb,
    strength FLOAT DEFAULT 0.3
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_working_owner ON jarvis_working_memory(owner);
CREATE INDEX IF NOT EXISTS idx_episodic_owner ON jarvis_episodic_memory(owner);
CREATE INDEX IF NOT EXISTS idx_semantic_owner ON jarvis_semantic_memory(owner);
CREATE INDEX IF NOT EXISTS idx_procedural_owner ON jarvis_procedural_memory(owner);

CREATE INDEX IF NOT EXISTS idx_working_timestamp ON jarvis_working_memory(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON jarvis_episodic_memory(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_episodic_importance ON jarvis_episodic_memory(importance DESC);
CREATE INDEX IF NOT EXISTS idx_procedural_strength ON jarvis_procedural_memory(strength DESC);
"""
    
    st.code(setup_sql, language="sql")
    
    st.markdown("""
    ### 🔑 Secrets requis (.streamlit/secrets.toml)
    
    ```toml
    [groq]
    api_key = "gsk_..."
    
    [supabase]
    url = "https://xxx.supabase.co"
    key = "eyJ..."
    ```
    """)
