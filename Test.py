import streamlit as st
import os
import psutil
from codecarbon import EmissionsTracker

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="ATLAS - Simulateur d'Impact", page_icon="🌿", layout="wide")

# --- INITIALISATION DE LA MÉMOIRE (SESSION STATE) ---
if 'flash_res' not in st.session_state:
    st.session_state.flash_res = None

# --- FONCTIONS DE CALCUL ---

def detecter_techno_reseau():
    stats = psutil.net_if_stats()
    interfaces = stats.keys()
    for name in interfaces:
        if stats[name].isup:
            n = name.lower()
            if n == "lo": continue
            if any(key in n for key in ["eth", "enp", "eno", "en1", "en0", "en"]):
                return "Fibre"
    for name in interfaces:
        if stats[name].isup:
            n = name.lower()
            if any(key in n for key in ["wlan", "wifi", "wl"]):
                return "WiFi"
    return "WiFi"

def calculer_impact_flash(taille_mo, nb_tokens, techno, coeff_ia):
    coeffs_reseau = {"WiFi": 0.00001, "4G": 0.0001, "Fibre": 0.000007}
    e_reseau = taille_mo * coeffs_reseau.get(techno, 0.00001)
    e_ia = nb_tokens * coeff_ia 
    return e_reseau, e_ia

def calculer_conso_a_vide(cpu_cores, ram_gb, stockage_to, type_stockage):
    p_base_systeme = 40.0 
    p_cpu_idle = cpu_cores * 0.8
    p_ram_idle = (ram_gb / 32) * 2.0
    conso_disque_base = 5.0 if type_stockage == "SSD NVMe (Performant)" else 8.0
    p_stockage_idle = stockage_to * conso_disque_base
    return p_base_systeme + p_cpu_idle + p_ram_idle + p_stockage_idle

def estimer_conso_composants(gpu, cpu_cores, ram_gb, stockage_to, type_stockage):
    gpu_power_map = {
        "Standard (RTX 3060 - 12Go)": 150,
        "Recommandé (RTX 3080 - 24Go)": 320,
        "Haute Performance (A100)": 400
    }
    conso_w_par_to = 6.0 if type_stockage == "SSD NVMe (Performant)" else 12.0
    p_gpu = gpu_power_map[gpu]
    p_cpu = cpu_cores * 4  
    p_ram = (ram_gb / 32) * 5 
    p_stockage = stockage_to * conso_w_par_to
    return p_gpu + p_cpu + p_ram + p_stockage

def calculer_projection(puissance_w, duree_label):
    heures_map = {"1 Jour": 24, "1 Semaine": 168, "1 Mois": 720, "6 Mois": 4320, "1 An": 8760}
    heures = heures_map[duree_label]
    wh = puissance_w * heures
    kwh = wh / 1000
    co2_kg = kwh * 0.052 
    return wh, co2_kg

# --- INTERFACE SIDEBAR ---
st.sidebar.header("Configuration Serveur (Appel d'Offre)")

option_gpu = st.sidebar.selectbox(
    "Puissance GPU (Traitement IA)",
    ("Standard (RTX 3060 - 12Go)", "Recommandé (RTX 3080 - 24Go)", "Haute Performance (A100)")
)
coeffs_gpu = {"Standard (RTX 3060 - 12Go)": 0.00025, "Recommandé (RTX 3080 - 24Go)": 0.00035, "Haute Performance (A100)": 0.00060}
coeff_ia_actuel = coeffs_gpu[option_gpu]

cpu_choice = st.sidebar.select_slider("Nombre de cœurs CPU", options=[8, 16, 32], value=16)
ram_choice = st.sidebar.radio("Mémoire vive (RAM)", [32, 64], format_func=lambda x: f"{x} Go")
type_stockage_choice = st.sidebar.radio("Type de stockage", ("SSD NVMe (Performant)", "Disque dur (Scalable)"))
stockage_choice = st.sidebar.slider("Volume de stockage (To)", 1, 10, 2)

st.sidebar.markdown("---")
duree_projection = st.sidebar.selectbox("Durée de la projection", ["1 Jour", "1 Semaine", "1 Mois", "6 Mois", "1 An"])

# --- CORPS DE L'APPLICATION ---
st.title("Projet ATLAS : Simulateur d'Impact Énergétique")
st.write("Outil de mesure d'impact pour le CFA EnSup-LR (Réponse Appel d'Offre 2025)")

# --- 1. ANALYSER LE DOCUMENT FLASH ---
st.header("Analyser le document flash d'un")
uploaded_file = st.file_uploader("Déposez votre première de compétence (PDF, Image, Vidéo...)", type=['pdf', 'docx', 'png', 'jpg', 'mp4', 'mkv', 'avi', 'jpeg', 'mpeg4'])

if uploaded_file is not None:
    taille_mo = uploaded_file.size / (1024 * 1024)
    nom_fichier = uploaded_file.name
    
    if nom_fichier.lower().endswith(('.mp4', '.mkv', '.avi', '.mpeg4')):
        nb_tokens_ia = 5000 
        st.warning("Format vidéo détecté : Charge IA plus élevée.")
    else:
        nb_tokens_ia = 1500
        st.success("Document norme de détection.")

    techno_actuelle = detecter_techno_reseau()
    st.info(f"**Fichier :** {nom_fichier} | **Taille :** {taille_mo:.2f} Mo | **Réseau :** {techno_actuelle}")

    if st.button("LANCER L'ANALYSE D'IMPACT"):
        with st.spinner("Mesure en cours..."):
            tracker = EmissionsTracker(log_level="error", save_to_file=False)
            tracker.start()
            sum(i*i for i in range(10**7)) 
            tracker.stop()
            try:
                conso_pc_wh = tracker._total_energy.kWh * 1000
            except:
                conso_pc_wh = tracker._total_energy.kwh * 1000

        e_net, e_ia = calculer_impact_flash(taille_mo, nb_tokens_ia, techno_actuelle, coeff_ia_actuel)
        total_flash_wh = conso_pc_wh + e_net + e_ia
        co2_flash_g = total_flash_wh * 0.052

        # ON SAUVEGARDE DANS LA MÉMOIRE
        st.session_state.flash_res = {
            "total_wh": total_flash_wh,
            "co2_g": co2_flash_g,
            "tokens": nb_tokens_ia,
            "pc_wh": conso_pc_wh,
            "net_wh": e_net,
            "ia_wh": e_ia,
            "gpu": option_gpu,
            "net_type": techno_actuelle
        }

# --- AFFICHAGE DES RÉSULTATS FLASH (S'ILS EXISTENT EN MÉMOIRE) ---
if st.session_state.flash_res:
    res = st.session_state.flash_res
    st.markdown("## Résultats de l'analyse")
    col_res1, col_res2, col_res3 = st.columns(3)
    col_res1.metric("Énergie Totale", f"{res['total_wh']:.4f} Wh")
    col_res2.metric("Impact Carbone", f"{res['co2_g']:.4f} gCO2e")
    col_res3.metric("Tokens IA", res['tokens'])

    with st.expander("🔍 Voir le détail par poste de consommation"):
        st.write(f"- Consommation locale (votre PC) : {res['pc_wh']:.6f} Wh")
        st.write(f"- Impact réseau ({res['net_type']}) : {res['net_wh']:.6f} Wh")
        st.write(f"- Impact serveur IA ({res['gpu']}) : {res['ia_wh']:.6f} Wh")

    st.success("Cette mesure permet de répondre aux critères de transition écologique de l'OPCO ATLAS.")

st.markdown("---")

# --- 2. PROJECTION EN ACTIVITÉ ---
puissance_active_w = estimer_conso_composants(option_gpu, cpu_choice, ram_choice, stockage_choice, type_stockage_choice)
energie_active_wh, co2_active_kg = calculer_projection(puissance_active_w, duree_projection)

st.subheader(f"Projection de consommation en activité sur : {duree_projection}")
c1, c2, c3 = st.columns(3)
c1.metric("Puissance Active", f"{puissance_active_w:.1f} W")
c2.metric("Énergie Cumulée", f"{energie_active_wh/1000:.2f} kWh")
c3.metric("Impact Carbone", f"{co2_active_kg:.2f} kg CO2e")

st.markdown("---")

# --- 3. CONSOMMATION À VIDE (IDLE) ---
puissance_idle_w = calculer_conso_a_vide(cpu_choice, ram_choice, stockage_choice, type_stockage_choice)
energie_idle_wh, co2_idle_kg = calculer_projection(puissance_idle_w, duree_projection)

st.subheader(f"Analyse de la consommation à vide sur : {duree_projection}")
cv1, cv2, cv3 = st.columns(3)
cv1.metric("Puissance Idle", f"{puissance_idle_w:.1f} W")
cv2.metric("Énergie Gaspillée", f"{energie_idle_wh/1000:.2f} kWh")
cv3.metric("Impact Passif", f"{co2_idle_kg:.3f} kg CO2e")