#HACKATHON

from codecarbon import EmissionsTracker
import os
import math

def calcul_impact_total(taille_mo, nb_tokens, duree_stockage_jours=30, techno="WiFi"):
    # 1. Énergie Réseau (Wh)
    coeffs_reseau = {"WiFi": 0.00001, "4G": 0.0001, "Fibre": 0.000007}
    e_reseau = taille_mo * coeffs_reseau.get(techno, 0.00001)

    # 2. Énergie IA (Wh)
    e_ia = nb_tokens * 0.00035 
    
    # 3. Énergie Stockage (Wh)
    e_stockage = taille_mo * (0.0003 * (duree_stockage_jours / 365))
    
    # 4. Total
    impact_numerique = e_reseau + e_ia + e_stockage
    
    # Conversion CO2
    co2_total = (impact_numerique) * 0.052
    
    return {
        "e_reseau": e_reseau,
        "e_ia": e_ia,
        "e_stockage": e_stockage,
        "co2_g": co2_total
    }

if __name__ == "__main__":
    print("Simulateur de votre consommation énergitique a la suite de vos conversation avec l'ia")

    chemin = input("Entrez le chemin (path) du fichier à envoyer : ").strip().replace("'", "").replace('"', "")
    
    if os.path.exists(chemin):
        taille_octets = os.path.getsize(chemin)
        taille_mo = taille_octets / (1024 * 1024) # Conversion Octets -> Mo

        print(f"Fichier détecté : {taille_mo:.2f} Mo")
    else:
        print("Erreur : Le fichier est introuvable.")
        exit()