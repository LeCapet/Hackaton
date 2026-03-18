# logic.py

def calculer_impact_flash(taille_mo, nb_tokens, techno, coeff_ia):
    """
    Calcule l'énergie consommée par le transfert réseau et l'inférence IA.
    - taille_mo : poids du fichier
    - nb_tokens : volume de texte à traiter
    - techno : type de connexion (Fibre, WiFi...)
    - coeff_ia : multiplicateur d'énergie spécifique au modèle choisi
    """
    coeffs_reseau = {"WiFi": 0.00001, "4G": 0.0001, "Fibre": 0.000007}
    e_reseau = taille_mo * coeffs_reseau.get(techno, 0.00001)
    e_ia = nb_tokens * coeff_ia 
    return e_reseau, e_ia

def calculer_conso_a_vide(gpu, cpu_cores, ram_gb, stockage_to, type_stockage):
    """
    Estime la puissance (Watts) consommée par le serveur quand il est allumé 
    mais qu'il ne fait aucun calcul intensif (Idle).
    """
    p_carte_mere_idle = 20.0 
    gpu_idle_map = {
        "Standard (RTX 3060 - 12Go)": 12.0,
        "Recommandé (RTX 3080 - 24Go)": 18.0,
        "Haute Performance (A100)": 35.0
    }
    p_gpu_idle = gpu_idle_map[gpu]
    p_cpu_idle = cpu_cores * 0.8 # Consommation par cœur au repos
    p_ram_idle = (ram_gb / 32) * 2.0
    conso_disque_base = 5.0 if type_stockage == "SSD NVMe (Performant)" else 8.0
    p_stockage_idle = stockage_to * conso_disque_base
    return p_carte_mere_idle + p_gpu_idle + p_cpu_idle + p_ram_idle + p_stockage_idle

def estimer_conso_composants(gpu, cpu_cores, ram_gb, stockage_to, type_stockage):
    """
    Estime la puissance (Watts) consommée par le serveur lorsqu'il travaille 
    à pleine charge (Calcul IA, entraînement, etc.).
    """
    p_carte_mere_active = 50.0 
    gpu_power_map = {
        "Standard (RTX 3060 - 12Go)": 150,
        "Recommandé (RTX 3080 - 24Go)": 320,
        "Haute Performance (A100)": 400
    }
    conso_w_par_to = 6.0 if type_stockage == "SSD NVMe (Performant)" else 12.0
    p_gpu = gpu_power_map[gpu]
    p_cpu = cpu_cores * 4  # Consommation par cœur en charge
    p_ram = (ram_gb / 32) * 5 
    p_stockage = stockage_to * conso_w_par_to
    return p_carte_mere_active + p_gpu + p_cpu + p_ram + p_stockage

def calculer_projection(puissance_w, duree_label):
    """
    Convertit une puissance (W) en énergie (Wh), en CO2 et en Euros 
    selon une durée choisie (jour, mois, an).
    """
    heures_map = {"1 Jour": 24, "1 Semaine": 168, "1 Mois": 720, "6 Mois": 4320, "1 An": 8760}
    heures = heures_map[duree_label]
    wh = puissance_w * heures
    kwh = wh / 1000
    co2_kg = kwh * 0.052 # Moyenne gCO2/kWh en France
    cout_euro = kwh * 0.2065 # Tarif bleu moyen 2024/2025
    return wh, co2_kg, cout_euro