import threading
import time
from dataclasses import dataclass

from scapy.all import AsyncSniffer
from scapy.layers.inet import IP, TCP

from config import DNS_REFRESH_SECONDS, SNIFF_FILTER_TCP_PORT, TARGET_HOSTS
from network_info import (
    build_effective_target_ips,
    get_all_local_ipv4_addresses,
    ip_in_target_ranges,
)


@dataclass
class TrafficSnapshot:
    running: bool
    bytes_up: int
    bytes_down: int
    packets_up: int
    packets_down: int
    duration_seconds: float
    started_at: float | None
    stopped_at: float | None
    target_ips: list[str]


class ClaudeTrafficTracker:
    def __init__(self, target_ips: list[str]):
        self.target_ips = set(target_ips)
        self.local_ips = set()

        self.bytes_up = 0
        self.bytes_down = 0
        self.packets_up = 0
        self.packets_down = 0

        self.started_at = None
        self.stopped_at = None
        self.running = False

        self._sniffer = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._refresh_thread = None

    def _refresh_targets_loop(self):
        while not self._stop_event.wait(DNS_REFRESH_SECONDS):
            try:
                new_ips = set(build_effective_target_ips(TARGET_HOSTS))
                if new_ips:
                    with self._lock:
                        self.target_ips = new_ips
            except Exception:
                pass

    def _match_target(self, ip_addr: str) -> bool:
        with self._lock:
            current_targets = set(self.target_ips)
        return ip_addr in current_targets or ip_in_target_ranges(ip_addr)

    def _handle_packet(self, packet):
        if not packet.haslayer(IP) or not packet.haslayer(TCP):
            return

        ip_layer = packet[IP]
        src = getattr(ip_layer, "src", None)
        dst = getattr(ip_layer, "dst", None)
        if not src or not dst:
            return

        pkt_len = len(packet)

        with self._lock:
            local_ips = set(self.local_ips)

        if src in local_ips and self._match_target(dst):
            with self._lock:
                self.bytes_up += pkt_len
                self.packets_up += 1
            return

        if dst in local_ips and self._match_target(src):
            with self._lock:
                self.bytes_down += pkt_len
                self.packets_down += 1
            return

    def start(self):
        if self.running:
            return

        with self._lock:
            self.local_ips = get_all_local_ipv4_addresses()
            self.bytes_up = 0
            self.bytes_down = 0
            self.packets_up = 0
            self.packets_down = 0
            self.started_at = time.time()
            self.stopped_at = None

        self.running = True
        self._stop_event.clear()

        bpf_filter = f"tcp port {SNIFF_FILTER_TCP_PORT}"
        self._sniffer = AsyncSniffer(
            filter=bpf_filter,
            prn=self._handle_packet,
            store=False,
        )
        self._sniffer.start()

        self._refresh_thread = threading.Thread(
            target=self._refresh_targets_loop,
            daemon=True,
        )
        self._refresh_thread.start()

    def stop(self):
        if not self.running:
            return

        self.running = False
        self._stop_event.set()

        try:
            if self._sniffer is not None:
                self._sniffer.stop()
        except Exception:
            pass

        with self._lock:
            self.stopped_at = time.time()

    def get_snapshot(self) -> TrafficSnapshot:
        with self._lock:
            now = time.time()
            end = self.stopped_at if self.stopped_at is not None else now
            duration = 0.0
            if self.started_at is not None:
                duration = max(0.0, end - self.started_at)

            return TrafficSnapshot(
                running=self.running,
                bytes_up=self.bytes_up,
                bytes_down=self.bytes_down,
                packets_up=self.packets_up,
                packets_down=self.packets_down,
                duration_seconds=duration,
                started_at=self.started_at,
                stopped_at=self.stopped_at,
                target_ips=sorted(self.target_ips),
            )