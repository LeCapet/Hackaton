# app.py
import streamlit as st
import pandas as pd
from codecarbon import EmissionsTracker

# Importation de nos modules locaux
import logic
import utils
import styles

# 1. Configuration initiale de la page (Titre de l'onglet, icône, largeur)
st.set_page_config(page_title="Simulateur d'Impact Énergétique", page_icon="🌿", layout="wide")

# 2. Chargement du design (CSS)
styles.load_custom_css()

# 3. Initialisation de la mémoire pour garder les résultats affichés lors d'un clic
if 'flash_res' not in st.session_state:
    st.session_state.flash_res = None

# --- SECTION : BARRE LATÉRALE (SIDEBAR) ---
st.sidebar.header("Configuration Serveur")
# Choix du matériel par l'utilisateur
option_gpu = st.sidebar.selectbox("Puissance GPU", ("Standard (RTX 3060 - 12Go)", "Recommandé (RTX 3080 - 24Go)", "Haute Performance (A100)"))
cpu_choice = st.sidebar.select_slider("Nombre de cœurs CPU", options=[8, 16, 32], value=16)
ram_choice = st.sidebar.radio("RAM", [32, 64], format_func=lambda x: f"{x} Go")
type_stockage_choice = st.sidebar.radio("Stockage", ("SSD NVMe (Performant)", "Disque dur (évolutif)"))
stockage_choice = st.sidebar.slider("Volume (To)", 1, 10, 2)
duree_projection = st.sidebar.selectbox("Durée de la projection", ["1 Jour", "1 Semaine", "1 Mois", "6 Mois", "1 An"])

# --- SECTION : CORPS PRINCIPAL ---
st.title("Simulateur d'Impact Énergétique")
st.write("Outil de mesure d'impact pour le CFA EnSup-LR (Réponse Appel d'Offre 2025)")

# Création des deux onglets principaux
tab1, tab2 = st.tabs(["🔍 Analyse Flash Document", "📊 Projection d'Activité"])

# --- ONGLET 1 : ANALYSE FLASH ---
with tab1:
    st.header("Analyse flash d'un document")
    uploaded_file = st.file_uploader("Upload", type=['pdf', 'docx', 'png', 'jpg', 'mp4', 'mkv', 'avi'], label_visibility="collapsed")

    if uploaded_file:
        # Analyse des propriétés du fichier téléchargé
        taille_mo = uploaded_file.size / (1024 * 1024)
        is_video = uploaded_file.name.lower().endswith(('.mp4', '.mkv', '.avi'))
        
        # Définition du nombre de tokens (mots/segments) selon le type de fichier
        tokens_to_process = [15000, 75000] if is_video else [1500]
        
        # Détection automatique de la connexion internet
        techno_actuelle = utils.detecter_techno_reseau()
        st.info(f"**Fichier :** {uploaded_file.name} | **Taille :** {taille_mo:.2f} Mo")

        if st.button("LANCER L'ANALYSE COMPARATIVE"):
            with st.spinner("Calcul en cours..."):
                # Mesure réelle de la consommation CPU du PC actuel via CodeCarbon
                tracker = EmissionsTracker(log_level="error", save_to_file=False)
                tracker.start()
                sum(i*i for i in range(10**7)) # Tâche de calcul simulée
                tracker.stop()
                conso_pc_wh = tracker._total_energy.kWh * 1000

                # Comparaison entre différents modèles d'IA
                models = {"GLM (IA Local)": 0.00019, "ChatGPT": 0.0008, "Claude": 0.0008}
                comparison_data = []
                for name, coeff in models.items():
                    # Appel de la fonction de calcul dans logic.py
                    e_net, e_ia = logic.calculer_impact_flash(taille_mo, tokens_to_process[0], techno_actuelle, coeff)
                    total_wh = conso_pc_wh + e_net + e_ia
                    comparison_data.append({
                        "Modèle IA": name,
                        "Énergie Totale (Wh)": round(total_wh, 4),
                        "Équivalent carbone (gCO2e)": round(total_wh * 0.052, 4)
                    })
                st.session_state.flash_res = comparison_data

    # Affichage du tableau de résultats s'ils existent
    if st.session_state.flash_res:
        st.table(pd.DataFrame(st.session_state.flash_res).set_index('Modèle IA')) 

# --- ONGLET 2 : PROJECTION ---
with tab2:
    # Calcul des deux scénarios : En activité et À vide
    p_act = logic.estimer_conso_composants(option_gpu, cpu_choice, ram_choice, stockage_choice, type_stockage_choice)
    wh_a, co2_a, eur_a = logic.calculer_projection(p_act, duree_projection)
    
    st.subheader(f"Projection en activité ({duree_projection})")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Puissance", f"{p_act:.1f} W")
    a2.metric("Énergie", f"{wh_a/1000:.2f} kWh")
    a3.metric("CO2", f"{co2_a:.2f} kg")
    a4.metric("Coût", f"{eur_a:.2f} €")

    st.markdown("---")

    p_idle = logic.calculer_conso_a_vide(option_gpu, cpu_choice, ram_choice, stockage_choice, type_stockage_choice)
    wh_i, co2_i, eur_i = logic.calculer_projection(p_idle, duree_projection)
    
    st.subheader(f"Consommation à vide (Idle)")
    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Puissance", f"{p_idle:.1f} W")
    v2.metric("Énergie", f"{wh_i/1000:.2f} kWh")
    v3.metric("CO2", f"{co2_i:.3f} kg")
    v4.metric("Coût", f"{eur_i:.2f} €")