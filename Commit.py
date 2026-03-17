import psutil
import time
import os
import sys
import logging
import json
import mimetypes
from codecarbon import EmissionsTracker

logging.getLogger("codecarbon").setLevel(logging.CRITICAL)

class HackathonPCPerformanceTracker:
    def __init__(self):
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

    def stop(self):
        actual_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            self.tracker.stop()
        finally:
            sys.stdout = actual_stdout

    def get_metrics(self):
        energy_kwh = self.tracker._total_energy.kWh if self.tracker._total_energy else 0
        co2_kg = self.tracker._total_emissions if self.tracker._total_emissions else 0

        return {
            "energy_wh": energy_kwh * 1000,
            "co2_g": co2_kg * 1000
        }

ENERGY_COEFFICIENTS = {
    "text_per_1k_chars": 0.05,
    "image_per_mb": 0.3,
    "video_per_mb": 0.6,
    "document_per_mb": 0.1
}

def detect_file_type(file_path):
    mime, _ = mimetypes.guess_type(file_path)
    if mime:
        if mime.startswith("image"): return "image"
        elif mime.startswith("video"): return "video"
        elif mime.startswith("text"): return "document"
    return "document"

def get_file_size_mb(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)

def estimate_energy(text="", files=None):
    if files is None:
        files = []

    text_chars = len(text)
    text_energy_j = (text_chars / 1000) * ENERGY_COEFFICIENTS["text_per_1k_chars"]

    files_energy_j = 0
    files_details = []

    for f in files:
        if not os.path.exists(f):
            continue

        size_mb = get_file_size_mb(f)
        ftype = detect_file_type(f)
        energy = size_mb * ENERGY_COEFFICIENTS.get(ftype + "_per_mb", 0.1)

        files_energy_j += energy

        files_details.append({
            "name": os.path.basename(f),
            "type": ftype,
            "size_mb": round(size_mb, 2),
            "energy_j": round(energy, 4)
        })

    total_energy_j = text_energy_j + files_energy_j

    return {
        "text": {
            "characters": text_chars,
            "energy_j": round(text_energy_j, 4)
        },
        "files": files_details,
        "summary": {
            "files_energy_j": round(files_energy_j, 4),
            "total_energy_j": round(total_energy_j, 4)
        }
    }

if __name__ == "__main__":
    tracker = HackathonPCPerformanceTracker()
    tracker.start()

    try:
        # Lecture JSON depuis stdin (comme p.py)
        data = json.load(sys.stdin)
        user_text = data.get("message", "")
        files = data.get("files", [])

        # Estimation énergétique
        estimation = estimate_energy(user_text, files)

        # Attente courte pour laisser CodeCarbon mesurer
        time.sleep(2)

        # Récupération métriques réelles
        real_metrics = tracker.get_metrics()

        # Fusion des résultats
        output = {
            "estimation": estimation,
            "real_metrics": {
                "energy_wh": round(real_metrics["energy_wh"], 4),
                "co2_g": round(real_metrics["co2_g"], 4)
            }
        }

        print(json.dumps(output, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}))

    finally:
        tracker.stop()
