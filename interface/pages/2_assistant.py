import streamlit as st
import os
import json
from CONFIG import LANGUAGE, JSON_SAVE_DIR
from configuration._ui_custom.page_title import set_page_title
from configuration._ui_custom.custom_ui import custom_ui
from kernel.start_kernel import start_DELTA, delta_memory_save # Import de la mémoire Supabase

# Configuration de la page
set_page_title("DELTA-Assistant")
custom_ui()

# --- BARRE LATÉRALE ---
if st.sidebar.checkbox("🤖​Démarrer DELTA" if LANGUAGE == 'fr' else "🤖​Start DELTA", key='start_DELTA'):
    start_DELTA()

st.sidebar.markdown("<hr style='margin:0px;'>", unsafe_allow_html=True)

# Fonctions de gestion des fichiers JSON (Archives locales)
def load_conversation(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def list_conversations(directory=JSON_SAVE_DIR):
    if not os.path.exists(directory):
        return []
    return [''] + [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def rename_conversation(old_path, new_name):
    directory, _ = os.path.split(old_path)
    new_path = os.path.join(directory, new_name + '.json')
    os.rename(old_path, new_path)

def delete_conversation(file_path):
    os.remove(file_path)

def download_conversation(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        conversation = json.load(file)
    csv_content = ""
    for message in conversation:
        csv_content += f"{message['role']}: {message['content']}\n"
    st.sidebar.download_button(
        label="Télécharger CSV" if LANGUAGE == 'fr' else "Download CSV",
        data=csv_content,
        file_name=os.path.basename(file_path).replace('.json', '.csv'),
        mime='text/csv'
    )

# --- LOGIQUE DES CONVERSATIONS ---
conversations = list_conversations()
selected_conversation = st.sidebar.selectbox('Sélectionnez une conversation' if LANGUAGE == 'fr' else 
                                             'Select a conversation', conversations, key='selected_conversation')

# Initialisation de l'état de la session
if 'session_state' not in st.session_state:
    st.session_state.session_state = []

if selected_conversation:
    conversation_path = os.path.join(JSON_SAVE_DIR, selected_conversation)
    
    if 'selected_conversation_path' not in st.session_state or st.session_state.selected_conversation_path != conversation_path:
        st.session_state.session_state = []
        st.session_state.selected_conversation_path = conversation_path
        conversation = load_conversation(conversation_path)
        for message in conversation:
            st.session_state.session_state.append({"role": message["role"], "content": message["content"]})

# --- AFFICHAGE DU CHAT ---
for message in st.session_state.session_state:
    with st.chat_message(message['role']):
        st.write(message['content'])

# --- BARRE DE RECHERCHE (RÉACTIVÉE) ---
prompt = st.chat_input("Dites quelque chose à DELTA..." if LANGUAGE == 'fr' else "Say something to DELTA...")

if prompt:
    # 1. Affichage immédiat
    with st.chat_message("user"):
        st.write(prompt)
    
    # 2. Ajout à l'historique local
    st.session_state.session_state.append({"role": "user", "content": prompt})
    
    # 3. SAUVEGARDE DANS LA MÉMOIRE SUPABASE (Dossiers)
    # Si vous parlez de vous, DELTA classe dans 'Identité'
    if "Sezer" in prompt or "suis" in prompt:
        delta_memory_save(prompt, dossier="Identité")
        st.toast("Mémoire mise à jour : Identité 👤")
    else:
        # Sauvegarde par défaut dans Général
        delta_memory_save(prompt, dossier="Général")

# --- BOUTONS DE GESTION (Barre latérale) ---
if selected_conversation:
    if st.sidebar.button('Renommer' if LANGUAGE == 'fr' else "Rename"):
        new_name = st.sidebar.text_input('Nouveau nom' if LANGUAGE == 'fr' else 'New name')
        if new_name:
            rename_conversation(conversation_path, new_name)
            st.rerun()

    if st.sidebar.button('Supprimer' if LANGUAGE == 'fr' else 'Delete'):
        delete_conversation(conversation_path)
        st.rerun()

    download_conversation(conversation_path)
