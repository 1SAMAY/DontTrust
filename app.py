import random
import sys
import time
import tkinter as tk

try:
    import winsound
except Exception:  # pragma: no cover - non-Windows fallback
    winsound = None


BG = "#000000"
PANEL = "#050505"
TEXT = "#d8ffd8"
DIM = "#79b879"
GREEN = "#00ff66"
WARN = "#ffb84d"
ERROR = "#ff5c73"
WHITE = "#f4f7f4"
MONO = ("Consolas", 10)
MONO_BOLD = ("Consolas", 10, "bold")


def sound(kind):
    if winsound is None:
        return
    try:
        if kind == "alert":
            winsound.MessageBeep(winsound.MB_ICONHAND)
        elif kind == "warn":
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            winsound.Beep(540, 35)
    except Exception:
        pass


class AlertPopup(tk.Toplevel):
    def __init__(self, master, title, body, severity):
        super().__init__(master)
        self.master_app = master
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=BG)
        self.attributes("-topmost", True)

        width = 388
        height = 188
        x = 42 + (master.popup_index * 36) % max(120, master.winfo_screenwidth() - width - 64)
        y = 96 + (master.popup_index * 28) % max(120, master.winfo_screenheight() - height - 120)
        self.geometry(f"{width}x{height}+{x}+{y}")
        master.popup_index += 1

        accent = ERROR if severity == "danger" else WARN
        title_fg = "#fff3f5" if severity == "danger" else "#fff1d1"

        container = tk.Frame(self, bg=PANEL, bd=1, highlightthickness=1, highlightbackground=accent)
        container.pack(fill="both", expand=True)

        bar = tk.Frame(container, bg=accent, height=30)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Label(bar, text=title, bg=accent, fg="#120305", font=MONO_BOLD).pack(side="left", padx=10)
        tk.Button(
            bar,
            text="X",
            command=self.close,
            bg=accent,
            fg="#120305",
            bd=0,
            font=MONO_BOLD,
            activebackground=accent,
            activeforeground="#120305",
            cursor="hand2",
        ).pack(side="right", padx=8)

        body_frame = tk.Frame(container, bg=PANEL)
        body_frame.pack(fill="both", expand=True, padx=14, pady=12)

        tk.Label(
            body_frame,
            text=body,
            wraplength=340,
            justify="left",
            bg=PANEL,
            fg=WHITE,
            font=MONO,
        ).pack(anchor="w", fill="x")

        btn_row = tk.Frame(body_frame, bg=PANEL)
        btn_row.pack(side="bottom", fill="x", pady=(16, 0))

        for label in ("Ignore", "Fix now"):
            tk.Button(
                btn_row,
                text=label,
                command=self.close,
                bg="#111111",
                fg=title_fg,
                bd=0,
                font=MONO_BOLD,
                activebackground="#1a1a1a",
                activeforeground=title_fg,
                cursor="hand2",
                padx=12,
                pady=8,
            ).pack(side="left", expand=True, fill="x", padx=4)

        self.bind("<Escape>", lambda _e: self.close())
        self.after(8500, self.close)
        sound("alert" if severity == "danger" else "warn")

    def close(self):
        if self.winfo_exists():
            self.destroy()


class CmdBreachApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Administrator: Command Prompt")
        self.geometry("980x620")
        self.minsize(840, 540)
        self.configure(bg=BG)

        self.popup_index = 0
        self.running = False
        self.after_ids = []
        self._typing_after = None
        self._cursor_visible = True
        self._command_text = ""
        self._current_prompt = "C:\\Windows\\System32>"
        self._stages = []

        self._build_ui()
        self._wire_events()
        self._tick_clock()
        self._blink_cursor()
        self.after(120, self._center_window)
        self.after(500, self.start_simulation)

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.topbar = tk.Frame(self, bg="#050505", height=34, bd=0, highlightthickness=1, highlightbackground="#111111")
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.grid_propagate(False)
        self.topbar.grid_columnconfigure(1, weight=1)

        title_wrap = tk.Frame(self.topbar, bg="#050505")
        title_wrap.grid(row=0, column=0, sticky="w", padx=10)
        tk.Label(title_wrap, text="Command Prompt", bg="#050505", fg=TEXT, font=MONO_BOLD).pack(side="left")
        tk.Label(title_wrap, text=" - ", bg="#050505", fg=DIM, font=MONO).pack(side="left")
        tk.Label(title_wrap, text="Security Breach Simulation", bg="#050505", fg=DIM, font=MONO).pack(side="left")

        self.clock_label = tk.Label(self.topbar, text="--:--:--", bg="#050505", fg=DIM, font=MONO)
        self.clock_label.grid(row=0, column=1, sticky="e", padx=10)

        controls = tk.Frame(self.topbar, bg="#050505")
        controls.grid(row=0, column=2, sticky="e", padx=6)
        for label, cmd, color in (("_", self.iconify, "#111111"), ("[]", self._toggle_maximize, "#111111"), ("X", self.destroy, ERROR)):
            tk.Button(
                controls,
                text=label,
                command=cmd,
                bg=color,
                fg=TEXT,
                bd=0,
                cursor="hand2",
                font=MONO_BOLD,
                width=3,
                activebackground=color,
                activeforeground=TEXT,
            ).pack(side="left", padx=2)

        self.main = tk.Frame(self, bg=BG, bd=0)
        self.main.grid(row=1, column=0, sticky="nsew", padx=10, pady=(8, 10))
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        header = tk.Frame(self.main, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        header.grid_columnconfigure(0, weight=1)

        self.header_label = tk.Label(
            header,
            text="C:\\Windows\\System32> ",
            bg=BG,
            fg=GREEN,
            font=MONO_BOLD,
            anchor="w",
        )
        self.header_label.grid(row=0, column=0, sticky="w")

        self.status_label = tk.Label(
            header,
            text="READY  |  SIMULATION ACTIVE",
            bg=BG,
            fg=DIM,
            font=MONO,
            anchor="e",
        )
        self.status_label.grid(row=0, column=1, sticky="e")

        console_shell = tk.Frame(self.main, bg=PANEL, bd=1, highlightthickness=1, highlightbackground="#131313")
        console_shell.grid(row=1, column=0, sticky="nsew")
        console_shell.grid_rowconfigure(0, weight=1)
        console_shell.grid_columnconfigure(0, weight=1)

        self.console = tk.Text(
            console_shell,
            bg=BG,
            fg=TEXT,
            insertbackground=GREEN,
            selectbackground="#1e3d1f",
            selectforeground=WHITE,
            wrap="word",
            bd=0,
            highlightthickness=0,
            padx=12,
            pady=10,
            font=MONO,
        )
        self.console.grid(row=0, column=0, sticky="nsew")
        scroll = tk.Scrollbar(console_shell, command=self.console.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.console.configure(yscrollcommand=scroll.set)

        self.prompt_bar = tk.Frame(self.main, bg=BG)
        self.prompt_bar.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.prompt_bar.grid_columnconfigure(1, weight=1)

        self.prompt_label = tk.Label(self.prompt_bar, text=self._current_prompt, bg=BG, fg=GREEN, font=MONO_BOLD)
        self.prompt_label.grid(row=0, column=0, sticky="w")

        self.typing_label = tk.Label(self.prompt_bar, text="", bg=BG, fg=TEXT, font=MONO, anchor="w")
        self.typing_label.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.status_strip = tk.Frame(self.main, bg="#020202", bd=1, highlightthickness=1, highlightbackground="#101010")
        self.status_strip.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        for column in range(4):
            self.status_strip.grid_columnconfigure(column, weight=1)

        self.stat_title = tk.Label(self.status_strip, text="THREAT", bg="#020202", fg=TEXT, font=MONO_BOLD, anchor="w")
        self.stat_firewall = tk.Label(self.status_strip, text="FIREWALL 100%", bg="#020202", fg=DIM, font=MONO, anchor="w")
        self.stat_cred = tk.Label(self.status_strip, text="CREDENTIALS 12%", bg="#020202", fg=DIM, font=MONO, anchor="w")
        self.stat_leak = tk.Label(self.status_strip, text="LEAK 4%", bg="#020202", fg=DIM, font=MONO, anchor="w")
        self.stat_title.grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.stat_firewall.grid(row=0, column=1, sticky="w", padx=10, pady=6)
        self.stat_cred.grid(row=0, column=2, sticky="w", padx=10, pady=6)
        self.stat_leak.grid(row=0, column=3, sticky="w", padx=10, pady=6)

    def _wire_events(self):
        self.bind("<Escape>", lambda _e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<F11>", lambda _e: self._toggle_maximize())

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = max(0, (self.winfo_screenwidth() - width) // 2)
        y = max(0, (self.winfo_screenheight() - height) // 3)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _toggle_maximize(self):
        if self.state() == "zoomed":
            self.state("normal")
        else:
            self.state("zoomed")

    def _tick_clock(self):
        self.clock_label.configure(text=time.strftime("%H:%M:%S"))
        self.after(1000, self._tick_clock)

    def _blink_cursor(self):
        self._cursor_visible = not self._cursor_visible
        self._render_prompt()
        self.after(500, self._blink_cursor)

    def _render_prompt(self):
        cursor = "_" if self._cursor_visible else " "
        self.typing_label.configure(text=f"{self._command_text}{cursor}")

    def _schedule(self, delay_ms, callback):
        after_id = self.after(delay_ms, callback)
        self.after_ids.append(after_id)

    def _cancel_scheduled(self):
        for after_id in self.after_ids:
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        self.after_ids.clear()

    def _write(self, text, tag="normal"):
        self.console.insert("end", text + "\n", tag)
        self.console.see("end")

    def _set_status(self, firewall, cred, leak):
        self.stat_firewall.configure(text=f"FIREWALL {firewall}%")
        self.stat_cred.configure(text=f"CREDENTIALS {cred}%")
        self.stat_leak.configure(text=f"LEAK {leak}%")

    def _clear_console(self):
        self.console.delete("1.0", "end")
        for name, fg in (("normal", TEXT), ("dim", DIM), ("ok", GREEN), ("warn", WARN), ("error", ERROR), ("prompt", GREEN)):
            self.console.tag_configure(name, foreground=fg, font=MONO)
        self.console.tag_configure("bold", foreground=WHITE, font=MONO_BOLD)
        self.console.tag_configure("prompt", foreground=GREEN, font=MONO_BOLD)

    def _boot_sequence(self):
        self._clear_console()
        boot_lines = [
            ("Microsoft Windows [Version 10.0.19045.0]", "bold"),
            ("(c) Microsoft Corporation. All rights reserved.", "dim"),
            ("", "normal"),
            ("C:\\Windows\\System32> initializing security monitor...", "prompt"),
            ("C:\\Windows\\System32> loading breach simulation modules...", "prompt"),
        ]
        for line, tag in boot_lines:
            self._write(line, tag)
        self._add_alert("System notice: simulation mode armed.", "warn")

    def _add_alert(self, text, severity):
        if severity == "danger":
            self._write(f"[ERROR] {text}", "error")
        elif severity == "warn":
            self._write(f"[WARNING] {text}", "warn")
        else:
            self._write(f"[OK] {text}", "ok")
        sound("alert" if severity == "danger" else "warn")

    def _create_popup(self, message, severity="warn"):
        title = "Windows Security Alert" if severity == "danger" else "System Warning"
        AlertPopup(self, title, message, severity)

    def _type_command(self, text, on_done, speed=26):
        self._command_text = ""
        self._render_prompt()
        if self._typing_after is not None:
            try:
                self.after_cancel(self._typing_after)
            except Exception:
                pass
            self._typing_after = None

        def step(index=0):
            if index > len(text):
                self._command_text = ""
                self._render_prompt()
                if on_done:
                    on_done()
                return
            self._command_text = text[:index]
            self._render_prompt()
            self._typing_after = self.after(speed, lambda: step(index + 1))

        step()

    def _append_stage(self, prompt, command, outputs, popup, severity):
        self._write(f"{prompt}{command}", "prompt")
        for idx, (line, tag) in enumerate(outputs):
            self._schedule(180 + idx * 210, lambda l=line, t=tag: self._write(l, t))
        self._schedule(150 + len(outputs) * 220, lambda: self._create_popup(popup, severity))

    def start_simulation(self):
        if self.running:
            return
        self.running = True
        self._cancel_scheduled()
        self._boot_sequence()

        self._stages = [
            {
                "cmd": "net session /query",
                "outputs": [
                    ("Accessing secure server...", "dim"),
                    ("Detecting session: srv-omega.local", "ok"),
                    ("Firewall status: stable but under pressure.", "warn"),
                ],
                "popup": "Unauthorized access attempt detected.",
                "severity": "warn",
                "status": (100, 12, 4),
            },
            {
                "cmd": "route print --trace",
                "outputs": [
                    ("Bypassing firewall...", "warn"),
                    ("Route path mapped through 7 synthetic hops.", "dim"),
                    ("Remote fingerprint matched: unknown.", "error"),
                ],
                "popup": "Your security settings have changed without permission.",
                "severity": "danger",
                "status": (78, 28, 16),
            },
            {
                "cmd": "vault crack --mode fake",
                "outputs": [
                    ("Password cracking engine started...", "dim"),
                    ("Password cracked: ********", "ok"),
                    ("Credential vault exposure detected.", "error"),
                ],
                "popup": "Password vault exposure detected.",
                "severity": "danger",
                "status": (48, 66, 42),
            },
            {
                "cmd": "db breach --simulate",
                "outputs": [
                    ("Injecting harmless payload...", "warn"),
                    ("Database breach simulated.", "ok"),
                    ("Records copied: 4,209 synthetic rows", "dim"),
                ],
                "popup": "Potential exfiltration detected. Quarantine advised.",
                "severity": "warn",
                "status": (20, 94, 88),
            },
        ]

        self._schedule(700, self._run_next_stage)

    def _run_next_stage(self):
        if not self._stages or not self.running:
            self._write("Mission complete. Simulation ended safely.", "ok")
            self.status_label.configure(text="COMPLETE  |  SIMULATION SAFE")
            return

        stage = self._stages.pop(0)
        self._set_status(*stage["status"])
        self.status_label.configure(text="ACTIVE  |  BREACH IN PROGRESS")
        self._type_command(stage["cmd"], on_done=lambda s=stage: self._finish_stage(s), speed=random.randint(18, 30))

    def _finish_stage(self, stage):
        self._append_stage(
            self._current_prompt,
            stage["cmd"],
            stage["outputs"],
            stage["popup"],
            stage["severity"],
        )
        self._schedule(1900, self._run_next_stage)

    def panic_stop(self):
        self.running = False
        self._cancel_scheduled()
        if self._typing_after is not None:
            try:
                self.after_cancel(self._typing_after)
            except Exception:
                pass
            self._typing_after = None
        self._stages = []
        self._command_text = ""
        self._render_prompt()
        self.status_label.configure(text="PAUSED  |  SIMULATION STOPPED")
        self._write("Panic stop engaged. Popups cleared.", "warn")

    def run_scan(self):
        self._write("Running integrity scan...", "dim")
        self._write("No real threats were found in this simulation.", "ok")
        self._set_status(98, 16, 7)
        self._create_popup("Integrity scan complete. No real threats were found.", "warn")

    def lock_workstation(self):
        self._write("Workstation lock engaged.", "warn")
        self._write("Unauthorized attempts logged.", "dim")
        self._create_popup("Workstation locked. Unauthorized attempts logged.", "warn")


def main():
    app = CmdBreachApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
