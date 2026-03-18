import json
import os
import time
import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from config import APP_TITLE, SESSIONS_DIR, TARGET_HOSTS, UI_REFRESH_MS
from impact import compute_transport_impact
from network_info import (
    build_effective_target_ips,
    detect_access_type,
    estimate_hops,
    geolocate_ip,
    get_public_ip,
)
from tracker import ClaudeTrafficTracker


def bytes_to_mb(num_bytes: int) -> float:
    return num_bytes / (1024 ** 2)


class SaveSessionDialog(tk.Toplevel):
    def __init__(self, parent, on_save_callback):
        super().__init__(parent)
        self.title("Enregistrer la session")
        self.geometry("520x360")
        self.resizable(False, False)
        self.on_save_callback = on_save_callback

        self.transient(parent)
        self.grab_set()

        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Titre de la session :", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.title_entry = ttk.Entry(container)
        self.title_entry.pack(fill="x", pady=(4, 12))
        self.title_entry.focus_set()

        ttk.Label(container, text="Mini compte rendu :", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.report_text = tk.Text(container, height=12, wrap="word")
        self.report_text.pack(fill="both", expand=True, pady=(4, 12))

        buttons = ttk.Frame(container)
        buttons.pack(fill="x")

        ttk.Button(buttons, text="Annuler", command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(buttons, text="Enregistrer", command=self._save).pack(side="right")

    def _save(self):
        title = self.title_entry.get().strip()
        report = self.report_text.get("1.0", "end").strip()

        if not title:
            messagebox.showwarning("Titre requis", "Merci de saisir un titre pour la session.")
            return

        self.on_save_callback(title, report)
        self.destroy()


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("980x720")
        self.root.minsize(860, 620)

        self.tracker = None
        self.session_context = {}
        self.last_result = None

        self.chart_times = []
        self.chart_upload_mb = []
        self.chart_download_mb = []

        self.status_var = tk.StringVar(value="Prêt")
        self.hosts_var = tk.StringVar(value=", ".join(TARGET_HOSTS))
        self.target_ips_var = tk.StringVar(value="-")
        self.public_ip_var = tk.StringVar(value="-")
        self.local_link_var = tk.StringVar(value="-")
        self.interface_var = tk.StringVar(value="-")
        self.local_ip_var = tk.StringVar(value="-")
        self.ssid_var = tk.StringVar(value="-")
        self.hops_var = tk.StringVar(value="-")
        self.distance_var = tk.StringVar(value="-")
        self.upload_var = tk.StringVar(value="0.0000 MB")
        self.download_var = tk.StringVar(value="0.0000 MB")
        self.total_var = tk.StringVar(value="0.0000 MB")
        self.duration_var = tk.StringVar(value="0.0 s")
        self.energy_var = tk.StringVar(value="-")
        self.co2_var = tk.StringVar(value="-")

        self._build_ui()
        self._schedule_refresh()

    def _build_ui(self):
        outer = ttk.Frame(self.root)
        outer.pack(fill="both", expand=True)

        self.canvas_container = tk.Canvas(outer, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.canvas_container.yview)
        self.canvas_container.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas_container.pack(side="left", fill="both", expand=True)

        self.main = ttk.Frame(self.canvas_container, padding=14)
        self.canvas_window = self.canvas_container.create_window((0, 0), window=self.main, anchor="nw")

        self.main.bind("<Configure>", self._on_frame_configure)
        self.canvas_container.bind("<Configure>", self._on_canvas_configure)
        self.canvas_container.bind_all("<MouseWheel>", self._on_mousewheel)

        title = ttk.Label(self.main, text=APP_TITLE, font=("Segoe UI", 20, "bold"))
        title.pack(anchor="w", pady=(0, 12))

        controls = ttk.Frame(self.main)
        controls.pack(fill="x", pady=(0, 12))

        self.start_btn = ttk.Button(controls, text="START", command=self.start_session)
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = ttk.Button(controls, text="STOP", command=self.stop_session, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 8))

        self.save_btn = ttk.Button(controls, text="Enregistrer", command=self.open_save_dialog, state="disabled")
        self.save_btn.pack(side="left", padx=(0, 8))

        ttk.Label(controls, textvariable=self.status_var, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(12, 0))

        info_frame = ttk.LabelFrame(self.main, text="Contexte réseau", padding=10)
        info_frame.pack(fill="x", pady=(0, 12))

        self._add_info_row(info_frame, "Hôtes ciblés", self.hosts_var, 0)
        self._add_info_row(info_frame, "IP(s) Claude résolue(s)", self.target_ips_var, 1)
        self._add_info_row(info_frame, "IP publique source", self.public_ip_var, 2)
        self._add_info_row(info_frame, "Type d'accès", self.local_link_var, 3)
        self._add_info_row(info_frame, "Interface", self.interface_var, 4)
        self._add_info_row(info_frame, "IP locale", self.local_ip_var, 5)
        self._add_info_row(info_frame, "SSID", self.ssid_var, 6)
        self._add_info_row(info_frame, "Next hops estimés", self.hops_var, 7)
        self._add_info_row(info_frame, "Distance estimée", self.distance_var, 8)

        live_frame = ttk.LabelFrame(self.main, text="Mesure de session", padding=10)
        live_frame.pack(fill="x", pady=(0, 12))

        self._add_info_row(live_frame, "Upload", self.upload_var, 0)
        self._add_info_row(live_frame, "Download", self.download_var, 1)
        self._add_info_row(live_frame, "Volume total", self.total_var, 2)
        self._add_info_row(live_frame, "Durée", self.duration_var, 3)

        result_frame = ttk.LabelFrame(self.main, text="Impact estimé", padding=10)
        result_frame.pack(fill="x", pady=(0, 12))

        self._add_info_row(result_frame, "Énergie transport", self.energy_var, 0)
        self._add_info_row(result_frame, "CO2 transport", self.co2_var, 1)

        chart_frame = ttk.LabelFrame(self.main, text="Graphique temps réel (MB cumulés)", padding=10)
        chart_frame.pack(fill="x", pady=(0, 12))

        self.figure = Figure(figsize=(7.2, 2.4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Upload / Download")
        self.ax.set_xlabel("Temps (s)")
        self.ax.set_ylabel("MB")
        self.ax.grid(True)

        self.upload_line, = self.ax.plot([], [], label="Upload")
        self.download_line, = self.ax.plot([], [], label="Download")
        self.ax.legend()

        self.canvas_plot = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas_plot.get_tk_widget().pack(fill="x", expand=False)
        self.canvas_plot.draw()

        logs_frame = ttk.LabelFrame(self.main, text="Journal", padding=10)
        logs_frame.pack(fill="both", expand=True, pady=(0, 12))

        self.log_text = tk.Text(logs_frame, height=8, wrap="word")
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(state="disabled")

    def _on_frame_configure(self, event=None):
        self.canvas_container.configure(scrollregion=self.canvas_container.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas_container.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas_container.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _add_info_row(self, parent, label_text, variable, row):
        ttk.Label(parent, text=label_text + " :", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky="w", padx=(0, 12), pady=4
        )
        ttk.Label(parent, textvariable=variable).grid(
            row=row, column=1, sticky="w", pady=4
        )

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def reset_chart(self):
        self.chart_times = []
        self.chart_upload_mb = []
        self.chart_download_mb = []

        self.upload_line.set_data([], [])
        self.download_line.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas_plot.draw()

    def update_chart(self, elapsed_s: float, up_mb: float, down_mb: float):
        self.chart_times.append(elapsed_s)
        self.chart_upload_mb.append(up_mb)
        self.chart_download_mb.append(down_mb)

        max_points = 300
        if len(self.chart_times) > max_points:
            self.chart_times = self.chart_times[-max_points:]
            self.chart_upload_mb = self.chart_upload_mb[-max_points:]
            self.chart_download_mb = self.chart_download_mb[-max_points:]

        self.upload_line.set_data(self.chart_times, self.chart_upload_mb)
        self.download_line.set_data(self.chart_times, self.chart_download_mb)

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas_plot.draw()

    def start_session(self):
        if self.tracker is not None and self.tracker.running:
            return

        try:
            self.log("Résolution des IP Claude...")
            target_ips = build_effective_target_ips(TARGET_HOSTS)
            if not target_ips:
                raise RuntimeError("Aucune IP IPv4 Claude n'a pu être résolue.")

            self.log("Détection du type d'accès...")
            access_info = detect_access_type()

            self.log("Récupération de l'IP publique...")
            public_ip = get_public_ip()

            self.log("Géolocalisation approximative SRC...")
            src_geo = geolocate_ip(public_ip)

            self.log("Géolocalisation approximative DST...")
            dst_geo = geolocate_ip(target_ips[0])

            hops_info = estimate_hops(src_geo, dst_geo, access_info["access_type"])

            self.tracker = ClaudeTrafficTracker(target_ips)
            self.tracker.start()

            self.session_context = {
                "target_hosts": TARGET_HOSTS,
                "target_ips": target_ips,
                "access_info": access_info,
                "public_ip": public_ip,
                "src_geo": src_geo,
                "dst_geo": dst_geo,
                "hops_info": hops_info,
                "started_at_iso": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            self.target_ips_var.set(", ".join(target_ips))
            self.public_ip_var.set(public_ip)
            self.local_link_var.set(access_info.get("access_type", "-"))
            self.interface_var.set(access_info.get("interface_description") or access_info.get("interface_name") or "-")
            self.local_ip_var.set(access_info.get("local_ip", "-"))
            self.ssid_var.set(access_info.get("ssid", "-"))
            self.hops_var.set(str(hops_info["estimated_hops"]))
            self.distance_var.set(f"{hops_info['distance_km']} km")

            self.energy_var.set("-")
            self.co2_var.set("-")
            self.upload_var.set("0.0000 MB")
            self.download_var.set("0.0000 MB")
            self.total_var.set("0.0000 MB")
            self.duration_var.set("0.0 s")
            self.save_btn.configure(state="disabled")
            self.last_result = None

            self.reset_chart()

            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.status_var.set("Mesure en cours")
            self.log("Capture démarrée.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self.log(f"Erreur au démarrage : {e}")

    def stop_session(self):
        if self.tracker is None or not self.tracker.running:
            return

        try:
            self.tracker.stop()
            snapshot = self.tracker.get_snapshot()

            hops_info = self.session_context["hops_info"]
            access_info = self.session_context["access_info"]

            impact = compute_transport_impact(
                bytes_up=snapshot.bytes_up,
                bytes_down=snapshot.bytes_down,
                estimated_hops=hops_info["estimated_hops"],
                access_type=access_info["access_type"],
            )

            self.energy_var.set(f"{impact.energy_wh:.4f} Wh")
            self.co2_var.set(f"{impact.co2_g:.4f} gCO2e")

            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.save_btn.configure(state="normal")
            self.status_var.set("Session terminée")

            self.last_result = {
                "session_context": self.session_context,
                "snapshot": {
                    "running": snapshot.running,
                    "bytes_up": snapshot.bytes_up,
                    "bytes_down": snapshot.bytes_down,
                    "packets_up": snapshot.packets_up,
                    "packets_down": snapshot.packets_down,
                    "duration_seconds": snapshot.duration_seconds,
                    "started_at": snapshot.started_at,
                    "stopped_at": snapshot.stopped_at,
                    "target_ips": snapshot.target_ips,
                },
                "impact": {
                    "total_bytes": impact.total_bytes,
                    "total_mb": impact.total_mb,
                    "total_gb": impact.total_gb,
                    "energy_kwh": impact.energy_kwh,
                    "energy_wh": impact.energy_wh,
                    "co2_g": impact.co2_g,
                    "access_factor": impact.access_factor,
                    "hops_factor": impact.hops_factor,
                },
                "user_notes": {
                    "title": "",
                    "report": "",
                },
                "stopped_at_iso": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            self.log("Capture arrêtée.")
            self.log(
                f"Résultat : {impact.total_mb:.4f} MB total | "
                f"{impact.energy_wh:.4f} Wh | {impact.co2_g:.4f} gCO2e"
            )
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self.log(f"Erreur à l'arrêt : {e}")

    def open_save_dialog(self):
        if not self.last_result:
            messagebox.showwarning("Aucune session", "Aucune session terminée à enregistrer.")
            return

        SaveSessionDialog(self.root, self.save_session_with_notes)

    def save_session_with_notes(self, title: str, report: str):
        if not self.last_result:
            return

        self.last_result["user_notes"] = {
            "title": title,
            "report": report,
        }

        os.makedirs(SESSIONS_DIR, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in title).strip("_")
        if not safe_title:
            safe_title = "session"

        filepath = os.path.join(SESSIONS_DIR, f"{timestamp}_{safe_title}.json")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.last_result, f, indent=2, ensure_ascii=False)

        self.log(f"Session enregistrée : {filepath}")
        messagebox.showinfo("Enregistrement OK", f"Session enregistrée dans :\n{filepath}")
        self.save_btn.configure(state="disabled")

    def _schedule_refresh(self):
        self._refresh_ui()
        self.root.after(UI_REFRESH_MS, self._schedule_refresh)

    def _refresh_ui(self):
        if self.tracker is None:
            return

        snapshot = self.tracker.get_snapshot()

        up_mb = bytes_to_mb(snapshot.bytes_up)
        down_mb = bytes_to_mb(snapshot.bytes_down)
        total_mb = up_mb + down_mb

        self.upload_var.set(f"{up_mb:.4f} MB")
        self.download_var.set(f"{down_mb:.4f} MB")
        self.total_var.set(f"{total_mb:.4f} MB")
        self.duration_var.set(f"{snapshot.duration_seconds:.1f} s")
        self.target_ips_var.set(", ".join(snapshot.target_ips) if snapshot.target_ips else "-")

        if snapshot.running:
            self.update_chart(snapshot.duration_seconds, up_mb, down_mb)


def main():
    root = tk.Tk()
    ttk.Style().theme_use("clam")
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()