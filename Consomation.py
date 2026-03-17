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
        # On redirige stdout vers devnull pour un silence total au lancement
        actual_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
        try:
            self.tracker = EmissionsTracker(
                project_name="Hackathon_CFA_EnSup",
                output_dir=".",
                measure_power_secs=1,
                save_to_file=False,
                log_level="error"
            )
        finally:
            sys.stdout = actual_stdout

    def start(self):
        actual_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            self.tracker.start()
        finally:
            sys.stdout = actual_stdout

    def get_and_display_metrics(self):
        # Recuperation des donnees brutes (kWh et kg)
        energy_kwh = self.tracker._total_energy.kWh if self.tracker._total_energy else 0
        co2_kg = self.tracker._total_emissions if self.tracker._total_emissions else 0

        # Conversions demandees
        energy_wh = energy_kwh * 1000
        co2_g = co2_kg * 1000

        # Rendu avec saut de ligne et nouvelles unites
        print(f"Energie Cumulee: {energy_wh:.4f} Wh\nCO2 rejete: {co2_g:.4f} g")
        print("-" * 30)
        
        return energy_wh, co2_g

# --- BOUCLE PRINCIPALE ---
my_tracker = HackathonPCPerformanceTracker()
my_tracker.start()

try:
    while True:
        my_tracker.get_and_display_metrics()
        time.sleep(2)
except KeyboardInterrupt:
    # On rend l'arret discret
    actual_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    my_tracker.tracker.stop()
    sys.stdout = actual_stdout
    print("\nArret du monitoring.")