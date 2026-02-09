import streamlit as st
import subprocess
from CONFIG import LANGUAGE, LLM_USE, LLM_DEFAULT_TO_PULL, LLM_EMBEDDING
from kernel.agent_llm.build_llm.auto_build_llm import build_the_model

def set_build_model():
    """
    Interface de construction du modèle DELTA.
    Force l'affichage du bouton de génération indépendamment de l'état actuel d'Ollama.
    """
    
    # 1. Vérification de l'état actuel d'Ollama
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        model_installed = LLM_USE in result.stdout
    except Exception:
        model_installed = False
        st.error("Ollama n'est pas détecté. Assurez-vous qu'il est lancé." if LANGUAGE == 'fr' else "Ollama not detected. Make sure it is running.")

    # 2. Affichage du statut au centre de l'écran
    if model_installed:
        st.success(f"✅ Le modèle **{LLM_USE}** est déjà configuré." if LANGUAGE == 'fr' else f"✅ Model **{LLM_USE}** is already configured.")
    else:
        st.info(f"💡 Le modèle **{LLM_USE}** doit être construit pour démarrer." if LANGUAGE == 'fr' else f"💡 Model **{LLM_USE}** needs to be built to start.")

    st.divider()

    # 3. LE BOUTON DE FORCE (Toujours visible sous le titre)
    if st.button("🚀 Lancer la construction de DELTA", use_container_width=True):
        with st.status("Construction en cours..." if LANGUAGE == 'fr' else "Building...", expanded=True) as status:
            
            # Étape A: Pull des modèles de base
            st.write("📥 Téléchargement des composants LLM..." if LANGUAGE == 'fr' else "📥 Downloading LLM components...")
            subprocess.run(['ollama', 'pull', LLM_DEFAULT_TO_PULL])
            subprocess.run(['ollama', 'pull', LLM_EMBEDDING])
            
            # Étape B: Création du Modelfile personnalisé via votre script
            st.write("🧠 Génération du cerveau de DELTA..." if LANGUAGE == 'fr' else "🧠 Generating DELTA's brain...")
            build_the_model()
            
            status.update(label="✅ DELTA est prêt Monsieur Sezer !" if LANGUAGE == 'fr' else "✅ DELTA is ready Monsieur Sezer!", state="complete", expanded=False)
        
        st.balloons()
        st.rerun() # Correction pour votre version de Streamlit