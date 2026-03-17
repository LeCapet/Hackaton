#HACKATHON
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
def calcul_impact_total(taille_mo, nb_tokens, techno, duree_stockage_jours=30):
    coeffs_reseau = {"WiFi": 0.00001, "4G": 0.0001, "Fibre": 0.000007}
    e_reseau = taille_mo * coeffs_reseau.get(techno, 0.00001)
    
    e_ia = nb_tokens * 0.00035 
    
    e_stockage = taille_mo * (0.0003 * (duree_stockage_jours / 365))
    
    impact_numerique = e_reseau + e_ia + e_stockage

    return {
        "e_reseau": e_reseau,
        "e_ia": e_ia,
        "e_stockage": e_stockage,
        "total_wh": impact_numerique,
        "co2_g": impact_numerique * 0.052
    }

if __name__ == "__main__":
    print("Simulateur de votre consommation énergitique a la suite de vos conversation avec l'ia")

    nb_tokens_ia = 0

    chemin = input("Chemin du fichier : ").strip().replace("'", "").replace('"', "")
    
    if os.path.exists(chemin):
        taille_mo = os.path.getsize(chemin) / (1024 * 1024)
        print(f"Fichier : {taille_mo:.2f} Mo")

        techno_actuelle = detecter_techno_reseau()
        print(f"Connexion : {techno_actuelle}")

        tracker = EmissionsTracker(log_level="error")
        tracker.start()
        
        print("Mesure en cours..")
        sum(i*i for i in range(10**7)) 
        
        tracker.stop()
        conso_pc_wh = tracker.final_emissions_data.energy_consumed * 1000

        res = calcul_impact_total(taille_mo, nb_tokens_ia, techno_actuelle)

        print("\n--- RÉSULTATS ---")
        print(f"Conso PC      : {conso_pc_wh:.6f} Wh")
        print(f"Conso Réseau  : {res['e_reseau']:.6f} Wh")
        print(f"Conso IA      : {res['e_ia']:.6f} Wh")
        print(f"Conso Stockage: {res['e_stockage']:.6f} Wh")
        print(f"TOTAL         : {conso_pc_wh + res['total_wh']:.4f} Wh")
        print(f"CO2           : {res['co2_g']:.4f} gCO2e")
    else:
        print("Erreur : Fichier introuvable.")