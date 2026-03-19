# styles.py
import streamlit as st

def load_custom_css():
    """
    Injecte du code CSS dans la page Streamlit pour :
    1. Centrer les textes dans les tableaux.
    2. Traduire les textes anglais par défaut du bouton de téléchargement.
    """
    st.markdown("""
        <style>
        /* Centrage global des tableaux */
        table { margin-left: auto; margin-right: auto; }
        th, td { text-align: center !important; }

        /* --- TRADUCTION DU DRAG & DROP EN FRANÇAIS --- */
        section[data-testid="stFileUploadDropzone"] div div { color: transparent; }
        section[data-testid="stFileUploadDropzone"] div div::before {
            content: "Glissez-déposez votre document ou vidéo ici";
            color: #31333F;
            display: block;
            margin-bottom: -20px;
        }
        section[data-testid="stFileUploadDropzone"] small { display: none; }
        section[data-testid="stFileUploadDropzone"] div div::after {
            content: "Limite de 200 Mo par fichier • PDF, DOCX, PNG, JPG, Vidéos";
            color: #808495;
            font-size: 0.8rem;
            display: block;
            margin-top: 10px;
        }
        /* --- CHANGEMENT DU BOUTON 'BROWSE FILES' --- */
        section[data-testid="stFileUploadDropzone"] button [data-testid="stMarkdownContainer"] p { display: none; }
        section[data-testid="stFileUploadDropzone"] button::after {
            content: "Choisir un fichier";
            display: block;
        }
        </style>
        """, unsafe_allow_html=True)