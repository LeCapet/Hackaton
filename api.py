# Projet Hackathon - CFA EnSup LR - Mars 2026
# Code permetant de faire les appels à l'API LM Studio pour obtenir des réponses à partir de messages et de fichiers

# ===== Importations des differéntes bibliotèques/codes nécessaires =====

import requests
import streamlit as st
from typing import Optional
from configuration import BASE_URL, API_KEY

# ===== Fonction pour faire une requete à l'API LM Studio =====

def demander_lmstudio(messages,
                      max_tokens: int = 2000,
                      temperature: float = 0.7) -> Optional[str]:
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "lm-studio",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=800
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except Exception as exc:
        st.error(f"Erreur API: {exc}")
        return None