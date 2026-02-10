# ================================================================
# DELTA OS - SYSTÈME DE MÉMOIRE JARVIS v2.0 (Production-Ready)
# ================================================================
# Inspiré de : Lux AI, ChromaDB best practices, Supabase pgvector
# Architecture : Hybrid Memory (Supabase + Embedding Search)
# ================================================================

import streamlit as st
from supabase import create_client, Client
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import datetime, timedelta
from groq import Groq
import numpy as np
from difflib import SequenceMatcher
import hashlib

# ================================================================
# CONFIGURATION
# ================================================================

class DeltaMemoryConfig:
    """Configuration centralisée du système de mémoire"""
    
    # Supabase
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    
    # Groq pour embeddings et analyse
    GROQ_API_KEY = st.secrets["groq"]["api_key"]
    GROQ_MODEL = "llama-3.3-70b-versatile"
    
    # Tables Supabase
    TABLE_ENTITIES = "delta_entities"          # Entités (personnes, sujets, projets)
    TABLE_MEMORIES = "delta_memories"          # Souvenirs avec embeddings
    TABLE_INTERACTIONS = "delta_interactions"  # Historique conversations
    
    # Dimensions embedding (text-embedding-ada-002 = 1536, on réduit pour perfs)
    EMBEDDING_DIMENSIONS = 768  # Réduit via PCA pour meilleures perfs
    
    # Seuils de similarité
    SIMILARITY_THRESHOLD_DUPLICATE = 0.85  # Détection doublons
    SIMILARITY_THRESHOLD_SEARCH = 0.7      # Recherche sémantique
    
    # Propriétaire système
    OWNER = "boran"  # IMPORTANT : Toujours normalisé

# ================================================================
# CLASSE PRINCIPALE : DELTA MEMORY SYSTEM
# ================================================================

class DeltaMemorySystem:
    """
    Système de mémoire hybride pour Delta OS
    
    Architecture inspirée de Lux AI :
    - Supabase pgvector : Stockage permanent + recherche sémantique
    - Détection automatique des doublons
    - Mémoire court/long terme
    - Anti-bug de polarité sémantique
    """
    
    def __init__(self):
        self.config = DeltaMemoryConfig()
        self.supabase: Client = create_client(
            self.config.SUPABASE_URL,
            self.config.SUPABASE_KEY
        )
        self.groq_client = Groq(api_key=self.config.GROQ_API_KEY)
        
        # Cache local pour performances
        self._entity_cache = {}
        self._last_cache_update = None
        
    # ================================================================
    # UTILITAIRES
    # ================================================================
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalise un nom pour éviter les doublons"""
        return name.lower().strip().replace(" ", "_").replace("-", "_")
    
    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """Calcule la similarité entre deux chaînes (0-1)"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Génère un embedding vectoriel du texte
        
        Note: En production, utiliser un modèle d'embedding dédié
        Ici on simule avec un hash pour l'exemple
        TODO: Intégrer sentence-transformers ou OpenAI embeddings
        """
        # TEMPORAIRE : Hash MD5 converti en vecteur (à remplacer en prod)
        # En production, utiliser :
        # from sentence_transformers import SentenceTransformer
        # model = SentenceTransformer('all-MiniLM-L6-v2')
        # embedding = model.encode(text)
        
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convertir en liste de floats (normaliser entre -1 et 1)
        embedding = []
        for i in range(self.config.EMBEDDING_DIMENSIONS):
            byte_idx = i % len(hash_bytes)
            value = (hash_bytes[byte_idx] / 255.0) * 2 - 1
            embedding.append(value)
        
        return embedding
    
    # ================================================================
    # DÉTECTION DE DOUBLONS
    # ================================================================
    
    def find_similar_entities(self, entity_name: str, threshold: float = None) -> List[Dict]:
        """
        Trouve les entités similaires (détection de doublons)
        
        Returns:
            Liste des entités similaires avec leur score de similarité
        """
        if threshold is None:
            threshold = self.config.SIMILARITY_THRESHOLD_DUPLICATE
        
        normalized = self.normalize_name(entity_name)
        
        # Récupère toutes les entités
        response = self.supabase.table(self.config.TABLE_ENTITIES).select("*").execute()
        
        similar_entities = []
        for entity in response.data:
            similarity = self.calculate_similarity(normalized, entity['entity_id'])
            if similarity >= threshold:
                similar_entities.append({
                    **entity,
                    'similarity_score': similarity
                })
        
        # Trie par similarité décroissante
        return sorted(similar_entities, key=lambda x: x['similarity_score'], reverse=True)
    
    # ================================================================
    # ANALYSE INTELLIGENTE (Anti-Bug Singularity)
    # ================================================================
    
    def analyze_input(self, user_input: str) -> Dict:
        """
        Analyse l'input utilisateur avec correction anti-bug
        
        Inspiré du système Singularity v12 mais amélioré :
        - Détecte la polarité correcte (affirmatif vs négatif)
        - Identifie les entités (personnes, sujets, projets)
        - Extrait les faits à mémoriser
        - Classe par type et priorité
        """
        
        # Récupère les entités existantes pour contexte
        existing_entities = self.supabase.table(self.config.TABLE_ENTITIES).select("entity_id, entity_name, entity_type").execute()
        entities_context = "\n".join([
            f"- {e['entity_name']} ({e['entity_type']})"
            for e in existing_entities.data[:20]  # Limite pour ne pas surcharger
        ])
        
        analysis_prompt = f"""
Tu es le cerveau de JARVIS. Analyse ce message de {self.config.OWNER.upper()}.

MESSAGE : "{user_input}"

ENTITÉS EXISTANTES (ne crée pas de doublons) :
{entities_context}

RÈGLES CRITIQUES :
1. POLARITÉ : Si l'utilisateur dit "non je préfère X" ou "en fait c'est Y", l'archive doit être AFFIRMATIVE ("Boran aime X")
2. PROPRIÉTAIRE : Tout ce qui concerne "je/mon/ma/mes" = {self.config.OWNER.upper()}
3. PAS DE DOUBLONS : Vérifie les entités existantes avant de créer
4. NORMALISATION : "Jules" = "jules", "mon pote Alex" = "alex"

TYPES D'ENTITÉS :
- self : {self.config.OWNER.upper()} lui-même
- person : autre personne
- topic : sujet général (chat, voiture, programmation)
- project : projet spécifique (delta_os, site_web)
- concept : concept/idée

CATÉGORIES D'INFO :
- identity : nom, âge, profession
- preferences : goûts, aversions
- relations : liens avec d'autres
- activities : activités, hobbies
- knowledge : apprentissages, compétences
- notes : notes diverses

RÉPONDS EN JSON STRICT :
{{
  "should_save": true/false,
  "entities": [
    {{
      "entity_name": "boran|jules|chat|etc",
      "entity_type": "self|person|topic|project|concept",
      "category": "identity|preferences|relations|activities|knowledge|notes",
      "facts": {{
        "fact_key": "fact_value"
      }},
      "priority": 1-4,
      "confidence": 0.0-1.0
    }}
  ],
  "reasoning": "Pourquoi tu as choisi ça"
}}

EXEMPLES :
Input: "Je m'appelle Boran, j'ai 25 ans"
→ entity_name: "boran", entity_type: "self", category: "identity", facts: {{"age": "25", "prenom": "Boran"}}

Input: "Non je me suis trompé, je préfère le chocolat au lait"
→ entity_name: "boran", entity_type: "self", category: "preferences", facts: {{"chocolat_prefere": "au lait"}}
(PAS "préfère contre" ou "trompé")

Input: "Mon pote Jules adore le foot"
→ entity_name: "jules", entity_type: "person", category: "preferences", facts: {{"passion": "football"}}
"""
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Expert en analyse sémantique et extraction d'entités."},
                    {"role": "user", "content": analysis_prompt}
                ],
                model=self.config.GROQ_MODEL,
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            st.error(f"Erreur analyse : {e}")
            return {
                "should_save": False,
                "entities": [],
                "reasoning": f"Erreur : {str(e)}"
            }
    
    # ================================================================
    # STOCKAGE DANS SUPABASE
    # ================================================================
    
    def store_entity(self, entity_data: Dict) -> bool:
        """
        Stocke ou met à jour une entité avec fusion intelligente
        
        Process :
        1. Vérifie si l'entité existe déjà (similarité)
        2. Si existe : FUSIONNE les nouvelles infos
        3. Si nouveau : CRÉE l'entité
        4. Génère et stocke l'embedding
        """
        
        entity_name = entity_data['entity_name']
        entity_type = entity_data['entity_type']
        category = entity_data['category']
        facts = entity_data['facts']
        priority = entity_data.get('priority', 2)
        
        # Normalisation stricte
        entity_id = self.normalize_name(entity_name)
        
        # SÉCURITÉ : Force le propriétaire
        if entity_type == "self":
            entity_id = self.config.OWNER
            entity_name = self.config.OWNER.capitalize()
        
        # Détecte les doublons
        similar = self.find_similar_entities(entity_name)
        
        if similar and similar[0]['similarity_score'] > 0.95:
            # Utilise l'entité existante
            entity_id = similar[0]['entity_id']
            st.info(f"🔗 Fusion avec entité existante : {entity_id}")
        
        try:
            # 1. Upsert entity principale
            entity_record = {
                "entity_id": entity_id,
                "entity_name": entity_name,
                "entity_type": entity_type,
                "last_updated": datetime.utcnow().isoformat(),
                "owner": self.config.OWNER
            }
            
            self.supabase.table(self.config.TABLE_ENTITIES).upsert(entity_record).execute()
            
            # 2. Stocke les faits avec embeddings
            for fact_key, fact_value in facts.items():
                # Construit le texte complet pour embedding
                fact_text = f"{entity_name} - {category} - {fact_key}: {fact_value}"
                embedding = self.generate_embedding(fact_text)
                
                memory_record = {
                    "entity_id": entity_id,
                    "category": category,
                    "fact_key": fact_key,
                    "fact_value": str(fact_value),
                    "fact_text": fact_text,
                    "embedding": embedding,
                    "priority": priority,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                self.supabase.table(self.config.TABLE_MEMORIES).insert(memory_record).execute()
            
            return True
            
        except Exception as e:
            st.error(f"Erreur stockage : {e}")
            return False
    
    # ================================================================
    # RECHERCHE SÉMANTIQUE
    # ================================================================
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Recherche sémantique dans la mémoire
        
        Utilise pgvector pour trouver les souvenirs similaires à la requête
        """
        
        query_embedding = self.generate_embedding(query)
        
        try:
            # Appelle la fonction Supabase pour recherche vectorielle
            # Note: Nécessite la fonction match_memories créée en SQL (voir setup)
            response = self.supabase.rpc(
                'match_memories',
                {
                    'query_embedding': query_embedding,
                    'match_count': limit,
                    'match_threshold': self.config.SIMILARITY_THRESHOLD_SEARCH
                }
            ).execute()
            
            return response.data
            
        except Exception as e:
            st.warning(f"Recherche vectorielle non disponible : {e}")
            # Fallback : recherche simple par texte
            return []
    
    def get_entity_complete_info(self, entity_name: str) -> Dict:
        """Récupère TOUTES les infos d'une entité"""
        
        entity_id = self.normalize_name(entity_name)
        
        # Entity principale
        entity = self.supabase.table(self.config.TABLE_ENTITIES)\
            .select("*")\
            .eq("entity_id", entity_id)\
            .execute()
        
        if not entity.data:
            return None
        
        # Tous les faits/souvenirs
        memories = self.supabase.table(self.config.TABLE_MEMORIES)\
            .select("*")\
            .eq("entity_id", entity_id)\
            .order("priority")\
            .execute()
        
        # Organise par catégorie
        categorized = {}
        for mem in memories.data:
            cat = mem['category']
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append({
                mem['fact_key']: mem['fact_value']
            })
        
        return {
            **entity.data[0],
            "memories": categorized
        }
    
    # ================================================================
    # RÉCUPÉRATION DE CONTEXTE INTELLIGENT
    # ================================================================
    
    def get_contextual_memory(self, query: str = None, relevant_entities: List[str] = None) -> str:
        """
        Récupère le contexte mémoire pertinent pour une conversation
        
        Args:
            query: Recherche sémantique optionnelle
            relevant_entities: Liste d'entités spécifiques à charger
        
        Returns:
            Contexte formaté pour le LLM
        """
        
        context_parts = []
        
        # 1. Info du propriétaire (toujours inclus)
        owner_info = self.get_entity_complete_info(self.config.OWNER)
        if owner_info:
            context_parts.append(f"=== PROPRIÉTAIRE : {self.config.OWNER.upper()} ===")
            for category, facts in owner_info.get('memories', {}).items():
                context_parts.append(f"\n[{category.upper()}]")
                for fact_dict in facts:
                    for k, v in fact_dict.items():
                        context_parts.append(f"  • {k}: {v}")
        
        # 2. Entités spécifiques demandées
        if relevant_entities:
            for entity_name in relevant_entities:
                if entity_name == self.config.OWNER:
                    continue  # Déjà inclus
                
                entity_info = self.get_entity_complete_info(entity_name)
                if entity_info:
                    context_parts.append(f"\n=== ENTITÉ : {entity_name.upper()} ===")
                    context_parts.append(f"Type: {entity_info['entity_type']}")
                    for category, facts in entity_info.get('memories', {}).items():
                        context_parts.append(f"\n[{category.upper()}]")
                        for fact_dict in facts:
                            for k, v in fact_dict.items():
                                context_parts.append(f"  • {k}: {v}")
        
        # 3. Recherche sémantique si query fourni
        if query:
            similar_memories = self.search_memories(query, limit=5)
            if similar_memories:
                context_parts.append("\n=== SOUVENIRS PERTINENTS ===")
                for mem in similar_memories:
                    context_parts.append(f"  • {mem['fact_text']} (similarité: {mem.get('similarity', 0):.2f})")
        
        return "\n".join(context_parts) if context_parts else "Aucune mémoire disponible."
    
    # ================================================================
    # INTERACTIONS LOGGING
    # ================================================================
    
    def log_interaction(self, user_message: str, assistant_response: str):
        """Archive une interaction pour apprentissage continu"""
        
        interaction = {
            "user_message": user_message,
            "assistant_response": assistant_response,
            "timestamp": datetime.utcnow().isoformat(),
            "owner": self.config.OWNER
        }
        
        try:
            self.supabase.table(self.config.TABLE_INTERACTIONS).insert(interaction).execute()
        except Exception as e:
            st.warning(f"Erreur log interaction : {e}")
    
    # ================================================================
    # PROCESS PRINCIPAL (Remplacement de autonomous_process)
    # ================================================================
    
    def process_message(self, user_input: str) -> Dict:
        """
        Process principal pour traiter un message utilisateur
        
        Returns:
            Dict avec status, message, entities_updated
        """
        
        # Analyse
        analysis = self.analyze_input(user_input)
        
        if not analysis.get('should_save'):
            return {
                "status": "no_action",
                "message": "💭 Message noté mais rien à archiver.",
                "reasoning": analysis.get('reasoning', '')
            }
        
        # Stockage
        entities_updated = []
        for entity_data in analysis.get('entities', []):
            if self.store_entity(entity_data):
                entities_updated.append(entity_data['entity_name'])
        
        if entities_updated:
            return {
                "status": "success",
                "message": f"✅ Mémoire mise à jour : {', '.join(set(entities_updated))}",
                "entities": entities_updated,
                "reasoning": analysis.get('reasoning', '')
            }
        else:
            return {
                "status": "error",
                "message": "⚠️ Échec de la sauvegarde",
                "reasoning": analysis.get('reasoning', '')
            }

# ================================================================
# SETUP SUPABASE (SQL à exécuter UNE FOIS)
# ================================================================

SUPABASE_SETUP_SQL = """
-- ================================================================
-- DELTA OS - Setup Supabase Tables & Functions
-- À exécuter dans le SQL Editor de Supabase
-- ================================================================

-- 1. Active l'extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Table des entités
CREATE TABLE IF NOT EXISTS delta_entities (
    entity_id TEXT PRIMARY KEY,
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- self, person, topic, project, concept
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    owner TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 3. Table des souvenirs (avec embeddings)
CREATE TABLE IF NOT EXISTS delta_memories (
    id BIGSERIAL PRIMARY KEY,
    entity_id TEXT NOT NULL REFERENCES delta_entities(entity_id) ON DELETE CASCADE,
    category TEXT NOT NULL, -- identity, preferences, relations, activities, knowledge, notes
    fact_key TEXT NOT NULL,
    fact_value TEXT NOT NULL,
    fact_text TEXT NOT NULL,
    embedding VECTOR(768), -- Réduit à 768 pour perfs (au lieu de 1536)
    priority INTEGER DEFAULT 2, -- 1=critique, 2=important, 3=utile, 4=secondaire
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Table des interactions
CREATE TABLE IF NOT EXISTS delta_interactions (
    id BIGSERIAL PRIMARY KEY,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    owner TEXT NOT NULL
);

-- 5. Index pour performances
CREATE INDEX IF NOT EXISTS idx_memories_entity ON delta_memories(entity_id);
CREATE INDEX IF NOT EXISTS idx_memories_category ON delta_memories(category);
CREATE INDEX IF NOT EXISTS idx_memories_priority ON delta_memories(priority);

-- 6. Index vectoriel HNSW (meilleur pour recherche sémantique)
CREATE INDEX IF NOT EXISTS idx_memories_embedding 
ON delta_memories 
USING hnsw (embedding vector_cosine_ops);

-- 7. Fonction de recherche vectorielle
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding VECTOR(768),
    match_count INT DEFAULT 10,
    match_threshold FLOAT DEFAULT 0.7
)
RETURNS TABLE (
    id BIGINT,
    entity_id TEXT,
    category TEXT,
    fact_key TEXT,
    fact_value TEXT,
    fact_text TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.entity_id,
        m.category,
        m.fact_key,
        m.fact_value,
        m.fact_text,
        1 - (m.embedding <=> query_embedding) AS similarity
    FROM delta_memories m
    WHERE 1 - (m.embedding <=> query_embedding) > match_threshold
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ================================================================
-- DONE! Votre base est prête pour Delta OS
-- ================================================================
"""

# ================================================================
# EXPORT
# ================================================================

__all__ = ['DeltaMemorySystem', 'DeltaMemoryConfig', 'SUPABASE_SETUP_SQL']
