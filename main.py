import streamlit as st

from configuration import PAGE_TITLE
from ui import init_session, sidebar
from api import demander_lmstudio
from gestion_fichiers import lire_fichier
from tracker import get_tracker

# =========================
# UI
# =========================
st.set_page_config(page_title=PAGE_TITLE, layout="wide")
st.title("Simulation IA Locale - Multi-Chat avec Fichiers")

# =========================
# SESSION
# =========================
init_session()

chat = st.session_state.chats[st.session_state.current_chat]

# =========================
# SIDEBAR
# =========================
max_tokens = sidebar(chat)

# =========================
# TRACKER
# =========================
tracker = get_tracker()

# =========================
# FILE UPLOAD
# =========================
uploaded_files = st.file_uploader(
    "Ajouts de fichiers",
    accept_multiple_files=True,
    type=["pdf", "docx", "xlsx", "csv", "txt"]
)

file_contents = ""

if uploaded_files:
    for file in uploaded_files:
        contenu = lire_fichier(file)
        file_contents += f"\n\n--- Fichier: {file.name} ---\n{contenu}\n"
        st.success(f"Fichier chargé : {file.name}")

# =========================
# HISTORIQUE
# =========================
for msg in chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# INPUT
# =========================
user_input = st.chat_input("Pose ta question...")

if user_input:

    if file_contents:
        user_input = f"""
Voici des fichiers à analyser :

{file_contents}

Question :
{user_input}
"""

    chat["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Réflexion en cours..."):
            tracker.start()

            réponse = demander_lmstudio(chat["messages"], max_tokens)

            emissions = tracker.stop()
            chat["emissions"] += emissions

            if réponse:
                st.markdown(réponse)
                chat["messages"].append({
                    "role": "assistant",
                    "content": réponse
                })