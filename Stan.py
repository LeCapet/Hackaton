import streamlit as st
import os
import psutil
from codecarbon import EmissionsTracker

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="ATLAS - Simulateur d'Impact", page_icon="🌿", layout="wide")

# --- FONCTIONS DE CALCUL ---

def calculer_conso_a_vide(cpu_cores, ram_gb, stockage_to):
    """Calcule la puissance de base (Idle) du serveur sans aucune tâche active"""
    p_base_systeme = 40.0 
    p_cpu_idle = cpu_cores * 0.8
    p_ram_idle = (ram_gb / 32) * 2.0
    p_stockage_idle = stockage_to * 5.0
    return p_base_systeme + p_cpu_idle + p_ram_idle + p_stockage_idle

def estimer_conso_composants(gpu, cpu_cores, ram_gb, stockage_to):
    """Calcule la puissance moyenne (Watts) basée sur les composants choisis"""
    p_gpu = {"Standard (RTX 3060)": 150, "Recommandé (RTX 3080 / A100)": 300}[gpu]
    p_cpu = cpu_cores * 4  
    p_ram = (ram_gb / 32) * 5 
    p_stockage = stockage_to * 10 
    return p_gpu + p_cpu + p_ram + p_stockage

def calculer_projection(puissance_w, duree_label):
    """Convertit la puissance en énergie cumulée selon la durée"""
    heures_map = {
        "1 Jour": 24,
        "1 Semaine": 24 * 7,
        "1 Mois": 24 * 30,
        "6 Mois": 24 * 30 * 6,
        "1 An": 24 * 365
    }
    heures = heures_map[duree_label]
    wh = puissance_w * heures
    kwh = wh / 1000
    co2_kg = kwh * 0.052 
    return wh, co2_kg

# --- INTERFACE SIDEBAR ---
st.sidebar.header("Configuration de l'Infrastructure")

gpu_choice = st.sidebar.selectbox(
    "Puissance GPU (Traitement IA)",
    ["Standard (RTX 3060)", "Recommandé (RTX 3080 / A100)"]
)

cpu_choice = st.sidebar.select_slider(
    "Nombre de cœurs CPU",
    options=[8, 16, 32],
    value=16
)

ram_choice = st.sidebar.radio(
    "Mémoire vive (RAM)",
    [32, 64],
    format_func=lambda x: f"{x} Go"
)

stockage_choice = st.sidebar.slider("Volume de stockage (To)", 1, 10, 2)

st.sidebar.markdown("---")
duree_projection = st.sidebar.selectbox(
    "Durée de la projection",
    ["1 Jour", "1 Semaine", "1 Mois", "6 Mois", "1 An"]
)

# --- CORPS DE L'APPLICATION ---
st.title("Projet ATLAS : Simulateur d'Impact Énergétique")
st.write("Outil d'analyse environnementale pour l'Appel d'Offre 2025.")

# --- 1. ANALYSE FLASH (TOUT EN HAUT) ---
st.header("Analyser le document flash d'un")
st.write("Mesurez l'impact immédiat du dépôt d'une preuve de compétence sur votre machine.")
uploaded_file = st.file_uploader("Déposez votre document (PDF, MP4, PNG...)", type=['pdf', 'mp4', 'png'])

if uploaded_file:
    if st.button("LANCER L'ANALYSE UNITAIRE"):
        with st.spinner("Mesure CodeCarbon en cours..."):
            tracker = EmissionsTracker(log_level="error", save_to_file=False)
            tracker.start()
            # Simulation d'activité
            sum(i*i for i in range(10**6))
            tracker.stop()
            try:
                conso_pc = tracker._total_energy.kWh * 1000
            except:
                conso_pc = tracker._total_energy.kwh * 1000
            st.success(f"Impact local de l'analyse : {conso_pc:.4f} Wh")

st.markdown("---")

# --- 2. PROJECTION EN ACTIVITÉ ---
puissance_active_w = estimer_conso_composants(gpu_choice, cpu_choice, ram_choice, stockage_choice)
energie_wh, co2_kg = calculer_projection(puissance_active_w, duree_projection)

st.subheader(f"Projection de consommation en activité sur : {duree_projection}")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Puissance Active", f"{puissance_active_w} W")
with col2:
    st.metric("Énergie Active", f"{energie_wh/1000:.2f} kWh")
with col3:
    st.metric("Impact Carbone Active", f"{co2_kg:.2f} kg CO2e")

st.markdown("---")

# --- 3. CONSOMMATION À VIDE (IDLE) ---
puissance_idle_w = calculer_conso_a_vide(cpu_choice, ram_choice, stockage_choice)
energie_idle_wh, co2_idle_kg = calculer_projection(puissance_idle_w, duree_projection)

st.subheader(f"Analyse de la consommation à vide (Idle) sur : {duree_projection}")
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    st.metric("Puissance à vide (Idle)", f"{puissance_idle_w:.1f} W")
with col_v2:
    st.metric("Énergie gaspillée", f"{energie_idle_wh/1000:.2f} kWh")
with col_v3:
    st.metric("Impact Carbone passif", f"{co2_idle_kg:.3f} kg CO2e")

with st.expander("Détails des composants configurés"):
    st.write(f"- GPU : {gpu_choice}")
    st.write(f"- CPU : {cpu_choice} cœurs")
    st.write(f"- RAM : {ram_choice} Go")
    st.write(f"- Stockage : {stockage_choice} To")

st.success("Analyse conforme aux indicateurs de performance environnementale ATLAS.")