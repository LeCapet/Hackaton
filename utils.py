# utils.py
import psutil

def detecter_techno_reseau():
    """
    Scanne les cartes réseau actives de l'ordinateur.
    Si elle trouve 'eth' ou 'en', elle considère que c'est de la Fibre (Ethernet).
    Si elle trouve 'wlan' ou 'wifi', elle considère que c'est du WiFi.
    """
    stats = psutil.net_if_stats()
    interfaces = stats.keys()
    for name in interfaces:
        if stats[name].isup: # Si la carte est allumée
            n = name.lower()
            if n == "lo": continue # Ignore la boucle locale
            if any(key in n for key in ["eth", "enp", "eno", "en1", "en0", "en"]):
                return "Fibre"
    for name in interfaces:
        if stats[name].isup:
            n = name.lower()
            if any(key in n for key in ["wlan", "wifi", "wl"]):
                return "WiFi"
    return "WiFi" # Par défaut