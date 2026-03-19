import psutil
import time
import os
import sys
import logging
from codecarbon import EmissionsTracker 

# Suppression des logs systeme
logging.getLogger("codecarbon").setLevel(logging.CRITICAL)

class HackathonPCPerformanceTracker:
    def __init__(self):
        actual_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
        try:
            self.tracker = EmissionsTracker(
                project_name="Hackathon_CFA_EnSup",
                measure_power_secs=1,
                save_to_file=False,
                log_level="error"
            )
        finally:
            sys.stdout = actual_stdout
            # Coefficient France (0.052 kg/kWh soit 52g/kWh)
            # Vous pouvez ajuster cette valeur selon votre config.py
            self.CO2_COEFFICIENT = 52.0 

    def start(self):
        actual_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            self.tracker.start()
        finally:
            sys.stdout = actual_stdout

    def get_and_display_metrics(self):
        # Récupération de l'énergie (plus fiable en temps réel)
        energy_kwh = self.tracker._total_energy.kWh if self.tracker._total_energy else 0
        
        # Conversion en Wh
        energy_wh = energy_kwh * 1000

        # CALCUL MANUEL DU CO2 (pour éviter le blocage de CodeCarbon)
        # Energie (Wh) * coefficient (g/Wh)
        # Note : 52g/kWh = 0.052g/Wh
        co2_g = energy_wh * (self.CO2_COEFFICIENT / 1000)

        # Rendu
        print(f"Energie Cumulee: {energy_wh:.4f} Wh")
        print(f"CO2 rejete (est.): {co2_g:.4f} g")
        print("-" * 30)
        
        return energy_wh, co2_g

# --- BOUCLE PRINCIPALE ---
my_tracker = HackathonPCPerformanceTracker()
my_tracker.start()

print("Monitoring démarré... (Ctrl+C pour arrêter)\n")

try:
    while True:
        # Pour voir la valeur bouger, il faut que le PC travaille un peu
        # car en "idle", la consommation augmente très lentement.
        my_tracker.get_and_display_metrics()
        time.sleep(2)
except KeyboardInterrupt:
    actual_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    my_tracker.tracker.stop()
    sys.stdout = actual_stdout
    print("\nArret du monitoring.")