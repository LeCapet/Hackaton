# Projet Hackathon - CFA EnSup LR - Mars 2026
# Code permetant de gérer l'interface utilisateur de l'application StreamLit

import streamlit as st
import uuid
from conversion import co2_to_wh


def init_session():
    if "chats" not in st.session_state:
        st.session_state.chats = {}

    if "current_chat" not in st.session_state:
        chat_id = str(uuid.uuid4())
        st.session_state.chats[chat_id] = {
            "messages": [],
            "emissions": 0.0
        }
        st.session_state.current_chat = chat_id


def sidebar(chat):
    with st.sidebar:
        st.header("Chats")

        for chat_id in st.session_state.chats.keys():
            if st.button(f"Chat {chat_id[:8]}"):
                st.session_state.current_chat = chat_id
                st.rerun()

        if st.button("Nouveau chat"):
            new_id = str(uuid.uuid4())
            st.session_state.chats[new_id] = {
                "messages": [],
                "emissions": 0.0
            }
            st.session_state.current_chat = new_id
            st.rerun()

        st.divider()

        max_tokens = st.slider("Max tokens", 100, 2000, 512)

        st.divider()

        st.header("Énergie")
        co2 = chat["emissions"]
        wh = co2_to_wh(co2)

        st.write(f"CO₂ : {co2 * 1000:.6f} g")
        st.write(f"Énergie : {wh:.2f} Wh")

        if st.button("Reset chat"):
            chat["messages"] = []
            chat["emissions"] = 0.0
            st.rerun()

    return max_tokens