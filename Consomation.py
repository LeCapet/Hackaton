import streamlit as st
import os
import psutil
import pandas as pd
from codecarbon import EmissionsTracker

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Simulateur d'Impact Énergétique", page_icon="🌿", layout="wide")

# --- CSS POUR CENTRER LE TABLEAU ---
st.markdown("""
    <style>
    table {
        margin-left: auto;
        margin-right: auto;
    }
    th, td {
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

def calculer_conso_a_vide(gpu, cpu_cores, ram_gb, stockage_to, type_stockage):
    p_carte_mere_idle = 20.0 
    gpu_idle_map = {
        "Standard (RTX 3060 - 12Go)": 12.0,
        "Recommandé (RTX 3080 - 24Go)": 18.0,
        "Haute Performance (A100)": 35.0
    }
    p_gpu_idle = gpu_idle_map[gpu]
    p_cpu_idle = cpu_cores * 0.8
    p_ram_idle = (ram_gb / 32) * 2.0
    conso_disque_base = 5.0 if type_stockage == "SSD NVMe (Performant)" else 8.0
    p_stockage_idle = stockage_to * conso_disque_base
    return p_carte_mere_idle + p_gpu_idle + p_cpu_idle + p_ram_idle + p_stockage_idle

def estimer_conso_composants(gpu, cpu_cores, ram_gb, stockage_to, type_stockage):
    p_carte_mere_active = 50.0 
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
    return p_carte_mere_active + p_gpu + p_cpu + p_ram + p_stockage

def calculer_projection(puissance_w, duree_label):
    heures_map = {"1 Jour": 24, "1 Semaine": 168, "1 Mois": 720, "6 Mois": 4320, "1 An": 8760}
    heures = heures_map[duree_label]
    wh = puissance_w * heures
    kwh = wh / 1000
    co2_kg = kwh * 0.052 
    cout_euro = kwh * 0.2065
    return wh, co2_kg, cout_euro

# --- INTERFACE SIDEBAR ---
st.sidebar.header("Configuration Serveur")

option_gpu = st.sidebar.selectbox(
    "Puissance GPU du serveur",
    ("Standard (RTX 3060 - 12Go)", "Recommandé (RTX 3080 - 24Go)", "Haute Performance (A100)")
)

cpu_choice = st.sidebar.select_slider("Nombre de cœurs CPU", options=[8, 16, 32], value=16)
ram_choice = st.sidebar.radio("Mémoire vive (RAM)", [32, 64], format_func=lambda x: f"{x} Go")
type_stockage_choice = st.sidebar.radio("Type de stockage", ("SSD NVMe (Performant)", "Disque dur (évolutif)"))
stockage_choice = st.sidebar.slider("Volume de stockage (To)", 1, 10, 2)

st.sidebar.markdown("---")
duree_projection = st.sidebar.selectbox("Durée de la projection", ["1 Jour", "1 Semaine", "1 Mois", "6 Mois", "1 An"])

# --- CORPS DE L'APPLICATION ---
st.title("Simulateur d'Impact Énergétique")
st.write("Outil de mesure d'impact pour le CFA EnSup-LR (Réponse Appel d'Offre 2025)")

# --- 1. ANALYSER LE DOCUMENT FLASH ---
st.header("Analyse flash d'un document")

uploaded_file = st.file_uploader("Déposez votre document ou vidéo...", type=['pdf', 'docx', 'png', 'jpg', 'mp4', 'mkv', 'avi', 'jpeg', 'mpeg4'])

if uploaded_file is not None:
    taille_mo = uploaded_file.size / (1024 * 1024)
    nom_fichier = uploaded_file.name
    
    # Logique de tokens : 1500 base | Vidéo Min (15k) | Vidéo Max (75k)
    base_text_tokens = 1500
    if nom_fichier.lower().endswith(('.mp4', '.mkv', '.avi', '.mpeg4')):
        type_fichier = "Vidéo"
        tokens_min = base_text_tokens * 10
        tokens_max = base_text_tokens * 50
        nb_tokens_label = f"{tokens_min} - {tokens_max}"
        tokens_to_process = [tokens_min, tokens_max]
        is_video = True
    else:
        type_fichier = "Document (PDF/Image)"
        tokens_to_process = [base_text_tokens]
        nb_tokens_label = str(base_text_tokens)
        is_video = False
        
    techno_actuelle = detecter_techno_reseau()

    st.info(f"**Fichier :** {nom_fichier} | **Taille :** {taille_mo:.2f} Mo | **Réseau :** {techno_actuelle}")

    if st.button("LANCER L'ANALYSE COMPARATIVE"):
        with st.spinner("Analyse en cours..."):
            tracker = EmissionsTracker(log_level="error", save_to_file=False)
            tracker.start()
            sum(i*i for i in range(10**7)) 
            tracker.stop()
            try:
                conso_pc_wh = tracker._total_energy.kWh * 1000
            except:
                conso_pc_wh = tracker._total_energy.kwh * 1000

        # Modèles incluant GLM (IA Local)
        models = {
            "GLM (IA Local)": 0.00019,
            "ChatGPT": 0.0008,
            "Claude": 0.0008
        }
        
        comparison_data = []
        for name, coeff in models.items():
            results_wh = []
            results_co2 = []
            results_money = []
            
            for t_val in tokens_to_process:
                e_net, e_ia = calculer_impact_flash(taille_mo, t_val, techno_actuelle, coeff)
                total_wh = conso_pc_wh + e_net + e_ia
                results_wh.append(total_wh)
                results_co2.append(total_wh * 0.052)
                results_money.append((total_wh / 1000) * 0.2065 * 100)

            # Affichage de la plage V1 - V2
            if len(results_wh) > 1:
                val_wh = f"{round(results_wh[0], 3)} - {round(results_wh[1], 3)}"
                val_co2 = f"{round(results_co2[0], 3)} - {round(results_co2[1], 3)}"
                val_money = f"{round(results_money[0], 3)} - {round(results_money[1], 3)}"
            else:
                val_wh = round(results_wh[0], 5)
                val_co2 = round(results_co2[0], 5)
                val_money = round(results_money[0], 4)

            comparison_data.append({
                "Modèle IA": name,
                "Énergie Totale (Wh)": val_wh,
                "Équivalent carbone (gCO2e)": val_co2,
                "Coût Élec (centimes)": val_money
            })

        st.session_state.flash_res = {
            "comparison": comparison_data,
            "tokens": nb_tokens_label,
            "type": type_fichier,
            "is_video": is_video
        }

if st.session_state.flash_res:
    res = st.session_state.flash_res
    st.markdown(f"#### Votre fichier **{res['type']}** demande **{res['tokens']} tokens** pour être traité, cela consommera :")
    
    df = pd.DataFrame(res['comparison'])
    st.table(df.set_index('Modèle IA')) 
    
    if res['is_video']:
        st.caption("ℹ️ **Note :** La plage de valeurs correspond au scénario optimiste (V1 : analyse fluide) vs intensif (V2 : haute résolution/mouvement).")

st.markdown("---")

# --- 2. PROJECTION EN ACTIVITÉ ---
puissance_active_w = estimer_conso_composants(option_gpu, cpu_choice, ram_choice, stockage_choice, type_stockage_choice)
energie_active_wh, co2_active_kg, cout_active = calculer_projection(puissance_active_w, duree_projection)

st.subheader(f"Projection de consommation en activité sur : {duree_projection}")
a1, a2, a3, a4 = st.columns(4)
a1.metric("Puissance", f"{puissance_active_w:.1f} W")
a2.metric("Énergie", f"{energie_active_wh/1000:.2f} kWh")
a3.metric("Équivalent carbone", f"{co2_active_kg:.2f} kg CO2e")
a4.metric("Prix", f"{cout_active:.2f} €")

st.markdown("---")

# --- 3. CONSOMMATION À VIDE / IDLE ---
puissance_idle_w = calculer_conso_a_vide(option_gpu, cpu_choice, ram_choice, stockage_choice, type_stockage_choice)
energie_idle_wh, co2_idle_kg, cout_idle = calculer_projection(puissance_idle_w, duree_projection)

st.subheader(f"Analyse de la consommation à vide sur : {duree_projection}")
v1, v2, v3, v4 = st.columns(4)
v1.metric("Puissance", f"{puissance_idle_w:.1f} W")
v2.metric("Énergie", f"{energie_idle_wh/1000:.2f} kWh")
v3.metric("Équivalent carbone", f"{co2_idle_kg:.3f} kg CO2e")
v4.metric("Prix", f"{cout_idle:.2f} €")