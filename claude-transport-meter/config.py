APP_TITLE = "Claude Transport Meter"

TARGET_HOSTS = [
    "claude.ai",
    "www.claude.ai",
]

# Rafraîchissement DNS automatique pendant la session
DNS_REFRESH_SECONDS = 30

# Filet de sécurité si certaines IP changent
TARGET_IPV4_CIDRS = [
    "160.79.104.0/23",
]

# Capture réseau
SNIFF_FILTER_TCP_PORT = 443

# Rafraîchissement UI (ms)
UI_REFRESH_MS = 1000

# Modèle d'impact
BASE_KWH_PER_GB = 0.05
GRID_INTENSITY_G_PER_KWH = 494.0

ACCESS_FACTORS = {
    "ethernet": 1.00,
    "wifi": 1.10,
    "wifi_hotspot_suspected": 1.40,
    "unknown": 1.15,
}

REFERENCE_HOPS = 15
HOPS_ALPHA = 0.05

SESSIONS_DIR = "sessions"