#!/usr/bin/env python3
import sys
import time
import threading
import subprocess
import json
import os
import platform
from datetime import datetime
from pathlib import Path

import psutil
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# ================= TERMS OF USE =================
TERMS = """
================= TERMS OF USE =================

This software functions as an interface for cryptocurrency mining.

• Mining consumes electricity and computer resources.
• All mining rewards belong exclusively to the user.
• The user must only run this software on devices they own
  or have explicit permission to use.
• The software does not collect, send, or redirect funds.
• The user is responsible for configuring their own wallet
  directly in the miner or mining pool.
• The author is not responsible for any damages, costs, or losses.

Click 'Accept' to continue or 'Decline' to exit.
"""

LOG_FILE = "miner_gui.log"

# Caminho do script e diretório de trabalho
SCRIPT_DIR = Path(__file__).resolve().parent
OS_SYSTEM = platform.system()

def find_xmrig():
    """Procura pelo executável do xmrig em múltiplos locais."""
    if OS_SYSTEM == "Windows":
        candidates = [
            SCRIPT_DIR / "xmrig.exe",
            SCRIPT_DIR / "xmrig-6.25.0" / "xmrig.exe",
            Path("xmrig.exe"),
        ]
    else:  # Linux, Mac, etc
        candidates = [
            SCRIPT_DIR / "xmrig",
            SCRIPT_DIR / "xmrig-6.25.0" / "xmrig",
            Path("xmrig"),
        ]
    
    for path in candidates:
        if path.exists():
            return path
    return None

XMRIG_PATH = find_xmrig()

# ================= LANGUAGE SYSTEM =================
LANG = "en"

TRANSLATIONS = {
    "en": {
        "control": "Control",
        "logs": "Logs",
        "system": "System",
        "wallet": "Wallet:",
        "cpu": "CPU:",
        "ram": "RAM:",
        "status_stopped": "Stopped",
        "status_mining": "Mining...",
    },
    "pt": {
        "control": "Controlo",
        "logs": "Registos",
        "system": "Sistema",
        "wallet": "Carteira:",
        "cpu": "CPU:",
        "ram": "RAM:",
        "status_stopped": "Parado",
        "status_mining": "A minerar...",
    },
    "es": {
        "control": "Control",
        "logs": "Registros",
        "system": "Sistema",
        "wallet": "Cartera:",
        "cpu": "CPU:",
        "ram": "RAM:",
        "status_stopped": "Detenido",
        "status_mining": "Minando...",
    }
}

def T(key: str) -> str:
    return TRANSLATIONS.get(LANG, TRANSLATIONS["en"]).get(key, key)

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

class MinerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Monero Auto-Miner")

        self.miner_process = None
        self.running = False

        self._build_terms_window()

    # ---------- Termos ----------
    def _build_terms_window(self):
        self.terms_win = tk.Toplevel(self.root)
        self.terms_win.title("User Terms")
        self.terms_win.grab_set()
        self.terms_win.protocol("WM_DELETE_WINDOW", self._on_terms_refuse)

        txt = tk.Text(self.terms_win, wrap="word", height=20, width=70)
        txt.insert("1.0", TERMS)
        txt.config(state="disabled")
        txt.pack(padx=10, pady=10)

        btn_frame = tk.Frame(self.terms_win)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Accept", command=self._on_terms_accept).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Decline", command=self._on_terms_refuse).pack(side="left", padx=5)

    def _on_terms_accept(self):
        self.terms_win.destroy()
        self._build_main_ui()

    def _on_terms_refuse(self):
        self.root.destroy()
        sys.exit(0)

    # ---------- UI principal ----------
    def _build_main_ui(self):
        main = ttk.Notebook(self.root, bootstyle="primary")
        main.pack(fill="both", expand=True)

        self.frame_control = ttk.Frame(main, padding=10)
        self.frame_log = ttk.Frame(main, padding=10)
        self.frame_system = ttk.Frame(main, padding=10)

        main.add(self.frame_control, text=T("control"))
        main.add(self.frame_log, text=T("logs"))
        main.add(self.frame_system, text=T("system"))

        self._build_control_tab()
        self._build_log_tab()
        self._build_system_tab()

    # ---------- Aba de controlo ----------
    def _build_control_tab(self):
        frame = self.frame_control

        ttk.Label(frame, text=T("wallet")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.wallet_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.wallet_var, width=60)
        entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        entry.bind("<Return>", lambda e: self.start_mining_auto())

        ttk.Label(frame, text="Press ENTER after typing wallet").grid(row=1, column=0, columnspan=2, pady=10)

        self.status_var = tk.StringVar(value=T("status_stopped"))
        ttk.Label(frame, textvariable=self.status_var, foreground="blue").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5
        )

    # ---------- Aba de logs ----------
    def _build_log_tab(self):
        frame = self.frame_log
        self.log_text = tk.Text(frame, wrap="word")
        self.log_text.pack(fill="both", expand=True)

    def append_log(self, msg: str):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")

    # ---------- Aba de sistema ----------
    def _build_system_tab(self):
        frame = self.frame_system

        self.cpu_var = tk.StringVar()
        self.ram_var = tk.StringVar()

        ttk.Label(frame, text=T("cpu")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, textvariable=self.cpu_var).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(frame, text=T("ram")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(frame, textvariable=self.ram_var).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self._update_system_stats()

    def _update_system_stats(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        self.cpu_var.set(f"{cpu:.1f}%")
        self.ram_var.set(f"{ram:.1f}%")
        self.root.after(1000, self._update_system_stats)

    # ---------- Mineração automática ----------
    def start_mining_auto(self):
        if self.running:
            return

        wallet = self.wallet_var.get().strip()
        if not wallet:
            messagebox.showerror("Erro", "Please enter your Monero wallet.")
            return

        # Verifica se o xmrig existe
        if not XMRIG_PATH:
            so = "Windows" if OS_SYSTEM == "Windows" else "Linux/Mac"
            instrucoes = (
                "xmrig não foi encontrado!\n\n"
                f"Sistema detectado: {so}\n\n"
                "Instruções:\n"
                "1. Descarrega de: https://github.com/xmrig/xmrig/releases\n"
                f"2. Extrai na pasta: {SCRIPT_DIR}\n"
                "3. O executável deve chamar-se 'xmrig' ou 'xmrig.exe'\n\n"
                "Depois tenta de novo!"
            )
            messagebox.showerror("Erro - xmrig não encontrado", instrucoes)
            log(f"xmrig não encontrado no sistema {OS_SYSTEM}")
            return

        pool = "stratum+tcp://pool.supportxmr.com:3333"
        worker = "autoWorker"

        cmd = [
            str(XMRIG_PATH),
            "-o", pool,
            "-u", f"{wallet}.{worker}",
            "-k",
            "--threads=1"
        ]

        try:
            self.miner_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Error starting miner: {e}")
            log(f"Erro ao iniciar minerador: {e}")
            return

        self.running = True
        self.status_var.set(T("status_mining"))
        log("Mining started.")
        self.append_log("Mining started.")

        threading.Thread(target=self._read_miner_output, daemon=True).start()

    def _read_miner_output(self):
        if not self.miner_process or not self.miner_process.stdout:
            return
        for line in self.miner_process.stdout:
            if not self.running:
                break
            line = line.strip()
            if line:
                log(f"MINER: {line}")
                self.append_log(f"MINER: {line}")

def main():
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()

    root = ttk.Window(themename="darkly")
    root.withdraw()
    app = MinerGUI(root)
    root.deiconify()
    root.mainloop()

if __name__ == "__main__":
    main()
