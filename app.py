# app.py
import streamlit as st
import pandas as pd
from codecarbon import EmissionsTracker

# Importation de nos modules locaux
import logic
import utils
import styles

# 1. Configuration initiale de la page (Titre de l'onglet, icone, largeur)
st.set_page_config(page_title="Simulateur d'Impact Energetique", page_icon="🌿", layout="wide")

# 2. Chargement du design (CSS)
styles.load_custom_css()

# 3. Initialisation de la memoire pour garder les resultats affiches
if 'flash_res' not in st.session_state:
    st.session_state.flash_res = None

# --- SECTION : BARRE LATERALE (SIDEBAR) ---
st.sidebar.header("Configuration Serveur")
option_gpu = st.sidebar.selectbox("Puissance GPU", ("Standard (RTX 3060 - 12Go)", "Recommande (RTX 3080 - 24Go)", "Haute Performance (A100)"))
cpu_choice = st.sidebar.select_slider("Nombre de coeurs CPU", options=[8, 16, 32], value=16)
ram_choice = st.sidebar.radio("RAM", [32, 64], format_func=lambda x: f"{x} Go")
type_stockage_choice = st.sidebar.radio("Stockage", ("SSD NVMe (Performant)", "Disque dur (evolutif)"))
stockage_choice = st.sidebar.slider("Volume (To)", 1, 10, 2)
duree_projection = st.sidebar.selectbox("Duree de la projection", ["1 Jour", "1 Semaine", "1 Mois", "6 Mois", "1 An"])

# --- SECTION : CORPS PRINCIPAL ---
st.title("Simulateur d'Impact Energetique")
st.write("Outil de mesure d'impact pour le CFA EnSup-LR (Reponse Appel d'Offre 2025)")

# Creation des deux onglets principaux
tab1, tab2 = st.tabs(["Analyse Flash Document", "Projection d'Activite"])

# --- ONGLET 1 : ANALYSE FLASH ---
with tab1:
    st.header("Analyse flash d'un document")
    uploaded_file = st.file_uploader("Upload", type=['pdf', 'docx', 'png', 'jpg', 'mp4', 'mkv', 'avi'], label_visibility="collapsed")

    if uploaded_file:
        taille_mo = uploaded_file.size / (1024 * 1024)
        is_video = uploaded_file.name.lower().endswith(('.mp4', '.mkv', '.avi'))
        
        # Definition des tokens (1500 PDF, 150000 max Video)
        tokens_to_process = [15000, 150000] if is_video else [1500]
        
        # Labels pour la phrase recapitulatrice
        type_label = "video" if is_video else "pdf"
        token_label = f"{tokens_to_process[0]} - {tokens_to_process[1]}" if is_video else f"{tokens_to_process[0]}"
        
        techno_actuelle = utils.detecter_techno_reseau()
        st.info(f"**Fichier :** {uploaded_file.name} | **Taille :** {taille_mo:.2f} Mo")

        if st.button("LANCER L'ANALYSE COMPARATIVE"):
            with st.spinner("Calcul en cours..."):
                tracker = EmissionsTracker(log_level="error", save_to_file=False)
                tracker.start()
                sum(i*i for i in range(10**7)) 
                tracker.stop()
                
                try:
                    conso_pc_wh = tracker._total_energy.kWh * 1000
                except:
                    conso_pc_wh = 0.05

                models = {"GLM (IA Local)": 0.00019, "ChatGPT": 0.0008, "Claude": 0.0008}
                comparison_data = []
                
                for name, coeff in models.items():
                    if is_video:
                        # Calcul Min (15 000 tokens)
                        e_net_min, e_ia_min = logic.calculer_impact_flash(taille_mo, tokens_to_process[0], techno_actuelle, coeff)
                        total_wh_min = conso_pc_wh + e_net_min + e_ia_min
                        
                        # Calcul Max (150 000 tokens)
                        e_net_max, e_ia_max = logic.calculer_impact_flash(taille_mo, tokens_to_process[1], techno_actuelle, coeff)
                        total_wh_max = conso_pc_wh + e_net_max + e_ia_max
                        
                        val_wh = f"{round(total_wh_min, 3)}-{round(total_wh_max, 3)}"
                        val_co2 = f"{round(total_wh_min * 0.052, 3)}-{round(total_wh_max * 0.052, 3)}"
                    else:
                        e_net, e_ia = logic.calculer_impact_flash(taille_mo, tokens_to_process[0], techno_actuelle, coeff)
                        total_wh = conso_pc_wh + e_net + e_ia
                        val_wh = round(total_wh, 4)
                        val_co2 = round(total_wh * 0.052, 4)

                    comparison_data.append({
                        "Modele IA": name,
                        "Energie Totale (Wh)": val_wh,
                        "Equivalent carbone (gCO2e)": val_co2
                    })
                
                st.session_state.flash_res = {
                    "data": comparison_data,
                    "type": type_label,
                    "tokens": token_label
                }

    if st.session_state.flash_res:
        res = st.session_state.flash_res
        st.markdown(f"### **Votre fichier {res['type']} a besoin de {res['tokens']} tokens pour l'analyser cela consommera :**")
        st.table(pd.DataFrame(res['data']).set_index('Modele IA')) 

# --- ONGLET 2 : PROJECTION ---
with tab2:
    p_act = logic.estimer_conso_composants(option_gpu, cpu_choice, ram_choice, stockage_choice, type_stockage_choice)
    wh_a, co2_a, eur_a = logic.calculer_projection(p_act, duree_projection)
    
    st.subheader(f"Projection en activite ({duree_projection})")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Puissance", f"{p_act:.1f} W")
    a2.metric("Energie", f"{wh_a/1000:.2f} kWh")
    a3.metric("CO2", f"{co2_a:.2f} kg")
    a4.metric("Cout", f"{eur_a:.2f} €")

    st.markdown("---")

    p_idle = logic.calculer_conso_a_vide(option_gpu, cpu_choice, ram_choice, stockage_choice, type_stockage_choice)
    wh_i, co2_i, eur_i = logic.calculer_projection(p_idle, duree_projection)
    
    st.subheader(f"Consommation a vide (Idle)")
    v1, v2, v3, v4 = st.columns(4)
    v1.metric("Puissance", f"{p_idle:.1f} W")
    v2.metric("Energie", f"{wh_i/1000:.2f} kWh")
    v3.metric("CO2", f"{co2_i:.3f} kg")
    v4.metric("Cout", f"{eur_i:.2f} €")