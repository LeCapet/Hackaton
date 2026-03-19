#HACKATHON
import streamlit as st
import os
import psutil
from codecarbon import EmissionsTracker

#Fonction qui détecte la technologie utilisé par l'utilisateur change la véritable consommation
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

# Fonction qui contient les différents calcul
def calcul_impact_total(taille_mo, nb_tokens, techno, coeff_ia, duree_stockage_jours=30):
    coeffs_reseau = {"WiFi": 0.00001, "4G": 0.0001, "Fibre": 0.000007}
    e_reseau = taille_mo * coeffs_reseau.get(techno, 0.00001)
    
    e_ia = nb_tokens * coeff_ia 
    
    e_stockage = taille_mo * (0.0003 * (duree_stockage_jours / 365))
    impact_numerique = e_reseau + e_ia + e_stockage

    return {
        "e_reseau": e_reseau,
        "e_ia": e_ia,
        "e_stockage": e_stockage,
        "total_wh": impact_numerique,
        "co2_g": impact_numerique * 0.052
    }

# --- CONFIGURATION DE LA PAGE WEB ---
st.set_page_config(page_title="ATLAS - Simulateur d'Impact", page_icon="🌿", layout="wide")

st.title("Projet ATLAS : Simulateur d'Impact Énergétique")
st.write("Outil de mesure d'impact pour le CFA EnSup-LR (Réponse Appel d'Offre 2025)")

# --- SIDEBAR : CHOIX DES COMPOSANTS ---
st.sidebar.header("Configuration Serveur (Appel d'Offre)")

option_gpu = st.sidebar.selectbox(
    "Puissance GPU (Traitement IA)",
    ("Standard (RTX 3060 - 12Go)", "Recommandé (RTX 3080 - 24Go)", "Haute Performance (A100)")
)

type_stockage = st.sidebar.radio("Type de stockage", ("SSD NVMe (Performant)", "HDD (Scalable)"))

st.sidebar.markdown("---")
duree_jours = st.sidebar.slider("Durée de stockage (jours)", 1, 365, 30)

# --- ZONE PRINCIPALE ---
uploaded_file = st.file_uploader("Déposez votre preuve de compétence (PDF, Image, Vidéo...)", type=['pdf', 'docx', 'png', 'jpg', 'mp4', 'mkv', 'avi'])

if uploaded_file is not None:
    taille_mo = uploaded_file.size / (1024 * 1024)
    nom_fichier = uploaded_file.name
    
    if nom_fichier.lower().endswith(('.mp4', '.mkv', '.avi')):
        nb_tokens_ia = 5000 
        st.warning("Format vidéo détecté : Le traitement IA demandera plus de ressources GPU.")
    else:
        nb_tokens_ia = 1500
        st.success("Document standard détecté.")

    techno_actuelle = detecter_techno_reseau()
    st.info(f"**Fichier :** {nom_fichier} | **Taille :** {taille_mo:.2f} Mo | **Réseau :** {techno_actuelle}")

    if st.button("LANCER L'ANALYSE D'IMPACT"):
        
        # --- FIX : On définit les coefficients ICI pour qu'ils changent vraiment ---
        coeffs_gpu = {
            "Standard (RTX 3060 - 12Go)": 0.00015, 
            "Recommandé (RTX 3080 - 24Go)": 0.00035, 
            "Haute Performance (A100)": 0.00080
        }
        coeff_ia_actuel = coeffs_gpu[option_gpu]

        with st.spinner("Mesure CodeCarbon en cours..."):
            tracker = EmissionsTracker(log_level="error")
            tracker.start()
            sum(i*i for i in range(10**7)) 
            tracker.stop()
            conso_pc_wh = tracker.final_emissions_data.energy_consumed * 1000

        res = calcul_impact_total(taille_mo, nb_tokens_ia, techno_actuelle, coeff_ia_actuel, duree_jours)
        total_wh = conso_pc_wh + res['total_wh']

        st.markdown("### Résultats de l'analyse")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Énergie Totale", f"{total_wh:.4f} Wh")
        c2.metric("Impact Carbone", f"{res['co2_g']:.4f} gCO2e")
        c3.metric("Tokens IA", nb_tokens_ia)

        with st.expander("🔍 Voir le détail par poste de consommation"):
            st.write(f"- **Consommation PC (Local) :** {conso_pc_wh:.6f} Wh")
            st.write(f"- **Transfert Réseau ({techno_actuelle}) :** {res['e_reseau']:.6f} Wh")
            st.write(f"- **Serveur IA ({option_gpu}) :** {res['e_ia']:.6f} Wh")
            st.write(f"- **Stockage ({type_stockage}) :** {res['e_stockage']:.6f} Wh")

        st.success("Cette mesure permet de répondre aux critères de transition écologique de l'OPCO ATLAS.")