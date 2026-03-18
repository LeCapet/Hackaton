import ipaddress
import platform
import shutil
import socket
import subprocess
from math import atan2, cos, radians, sin, sqrt

import psutil
import requests

from config import TARGET_IPV4_CIDRS


def run_command(cmd: list[str], timeout: int = 5) -> str:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            encoding="utf-8",
            errors="ignore",
        )
        return (result.stdout or "").strip()
    except Exception:
        return ""


def get_public_ip() -> str:
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=5)
        r.raise_for_status()
        data = r.json()
        return data.get("ip", "unknown")
    except Exception:
        return "unknown"


def geolocate_ip(ip: str) -> dict:
    # ip-api renvoie une géoloc approximative
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,countryCode,regionName,city,lat,lon",
            timeout=5,
        )
        data = r.json()
        if data.get("status") != "success":
            raise RuntimeError("geolocation failed")

        return {
            "ip": ip,
            "lat": float(data.get("lat", 0.0) or 0.0),
            "lon": float(data.get("lon", 0.0) or 0.0),
            "city": (data.get("city") or "").strip(),
            "country": (data.get("countryCode") or "").strip(),
            "continent": "",  # non fourni ici
            "region": (data.get("regionName") or "").strip(),
        }
    except Exception:
        return {
            "ip": ip,
            "lat": 0.0,
            "lon": 0.0,
            "city": "",
            "country": "",
            "continent": "",
            "region": "",
        }


def resolve_host_ips(host: str) -> list[str]:
    ips = set()
    try:
        infos = socket.getaddrinfo(host, 443, family=socket.AF_INET, type=socket.SOCK_STREAM)
        for info in infos:
            ip = info[4][0]
            if ip:
                ips.add(ip)
    except Exception:
        pass
    return sorted(ips)


def build_effective_target_ips(hosts: list[str]) -> list[str]:
    all_ips = set()
    for host in hosts:
        for ip in resolve_host_ips(host):
            all_ips.add(ip)
    return sorted(all_ips)


def ip_in_target_ranges(ip: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        return False

    for cidr in TARGET_IPV4_CIDRS:
        try:
            if ip_obj in ipaddress.ip_network(cidr, strict=False):
                return True
        except ValueError:
            continue

    return False


def get_local_ip_used_for_internet() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("1.1.1.1", 80))
        return s.getsockname()[0]
    except Exception:
        return ""
    finally:
        s.close()


def get_all_local_ipv4_addresses() -> set[str]:
    ips = set()

    for iface_name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address and not addr.address.startswith("127."):
                ips.add(addr.address)

    primary = get_local_ip_used_for_internet()
    if primary:
        ips.add(primary)

    return ips


def _find_interface_for_local_ip(local_ip: str) -> str:
    for iface_name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == local_ip:
                return iface_name
    return ""


def _get_ssid_windows() -> str:
    output = run_command(["netsh", "wlan", "show", "interfaces"], timeout=5)
    if not output:
        return "-"

    for line in output.splitlines():
        line_stripped = line.strip()
        if line_stripped.upper().startswith("SSID") and "BSSID" not in line_stripped.upper():
            parts = line_stripped.split(":", 1)
            if len(parts) == 2:
                value = parts[1].strip()
                return value or "-"
    return "-"


def _get_ssid_linux() -> str:
    if shutil.which("iwgetid"):
        output = run_command(["iwgetid", "-r"], timeout=3)
        return output or "-"
    return "-"


def _get_ssid_macos() -> str:
    airport = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    if shutil.which("networksetup"):
        output = run_command(["networksetup", "-getairportnetwork", "en0"], timeout=3)
        if ":" in output:
            return output.split(":", 1)[1].strip() or "-"
    if airport:
        output = run_command([airport, "-I"], timeout=3)
        for line in output.splitlines():
            if " SSID:" in line:
                return line.split("SSID:", 1)[1].strip() or "-"
    return "-"


def detect_access_type() -> dict:
    local_ip = get_local_ip_used_for_internet()
    iface_name = _find_interface_for_local_ip(local_ip) or "-"
    iface_lower = iface_name.lower()

    access_type = "unknown"
    ssid = "-"

    if any(x in iface_lower for x in ["wi-fi", "wifi", "wlan", "wireless", "sans fil"]):
        access_type = "wifi"
    elif any(x in iface_lower for x in ["ethernet", "eth", "enp", "eno", "lan"]):
        access_type = "ethernet"

    system = platform.system().lower()

    if access_type == "wifi":
        if system == "windows":
            ssid = _get_ssid_windows()
        elif system == "linux":
            ssid = _get_ssid_linux()
        elif system == "darwin":
            ssid = _get_ssid_macos()

        hotspot_keywords = [
            "iphone",
            "android",
            "hotspot",
            "partage",
            "sharing",
            "tether",
            "mobile",
            "galaxy",
            "redmi",
            "xiaomi",
            "huawei",
        ]
        if ssid != "-" and any(k in ssid.lower() for k in hotspot_keywords):
            access_type = "wifi_hotspot_suspected"

    return {
        "access_type": access_type,
        "interface_name": iface_name,
        "interface_description": iface_name,
        "local_ip": local_ip or "-",
        "ssid": ssid,
    }


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def estimate_hops(src_geo: dict, dst_geo: dict, access_type: str = "ethernet") -> dict:
    lat1 = src_geo.get("lat", 0.0) or 0.0
    lon1 = src_geo.get("lon", 0.0) or 0.0
    lat2 = dst_geo.get("lat", 0.0) or 0.0
    lon2 = dst_geo.get("lon", 0.0) or 0.0

    distance = haversine_km(lat1, lon1, lat2, lon2)

    access_penalty_map = {
        "ethernet": 2,
        "wifi": 3,
        "wifi_hotspot_suspected": 5,
        "unknown": 3,
    }
    access_penalty = access_penalty_map.get(access_type, 3)

    same_country = (
        src_geo.get("country")
        and dst_geo.get("country")
        and src_geo.get("country") == dst_geo.get("country")
    )

    if distance < 50:
        distance_bonus = 0
    elif distance < 300:
        distance_bonus = 1
    elif distance < 1000:
        distance_bonus = 2
    elif distance < 3000:
        distance_bonus = 3
    elif distance < 7000:
        distance_bonus = 4
    else:
        distance_bonus = 5

    geo_base = 5 if same_country else 12
    border_bonus = 0 if same_country else 2

    hops = access_penalty + geo_base + distance_bonus + border_bonus
    hops = max(4, min(hops, 30))

    return {
        "estimated_hops": hops,
        "distance_km": round(distance, 1),
        "access_type": access_type,
    }