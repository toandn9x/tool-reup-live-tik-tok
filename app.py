import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from tiktok_restreamer import TikTokRestreamer
import threading
import sys
import os
import json

# Set appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TikTok Live Restreamer v1.1")
        self.geometry("800x700")

        self.restreamer = None
        self.config_file = "config.json"

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(self, text="TikTok Live Restreamer", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Input Frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.input_frame.grid_columnconfigure(1, weight=1)

        # TikTok URLs
        self.url_label = ctk.CTkLabel(self.input_frame, text="TikTok URLs (one per line or comma separated):")
        self.url_label.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        self.url_text = ctk.CTkTextbox(self.input_frame, height=100)
        self.url_text.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.url_text.insert("1.0", "https://www.tiktok.com/@username/live")

        # RTMP Server
        self.rtmp_label = ctk.CTkLabel(self.input_frame, text="RTMP Server URL:")
        self.rtmp_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.rtmp_entry = ctk.CTkEntry(self.input_frame, placeholder_text="rtmp://a.rtmp.youtube.com/live2")
        self.rtmp_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Stream Key
        self.key_label = ctk.CTkLabel(self.input_frame, text="Stream Key:")
        self.key_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.key_entry = ctk.CTkEntry(self.input_frame, placeholder_text="xxxx-xxxx-xxxx-xxxx", show="*")
        self.key_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Auto-Switch Checkbox
        self.auto_switch_var = tk.BooleanVar(value=False)
        self.auto_switch_cb = ctk.CTkCheckBox(self.input_frame, text="Enable Auto-Switch (Scan list & restart on end)", variable=self.auto_switch_var)
        self.auto_switch_cb.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Affiliate Link / Overlay Text
        self.overlay_label = ctk.CTkLabel(self.input_frame, text="Affiliate Link / Overlay Text:")
        self.overlay_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.overlay_entry = ctk.CTkEntry(self.input_frame, placeholder_text="e.g. Link mua hàng: bit.ly/my-shop")
        self.overlay_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Cookie File
        self.cookie_label = ctk.CTkLabel(self.input_frame, text="Cookie File (Optional):")
        self.cookie_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.cookie_path = tk.StringVar()
        self.cookie_entry = ctk.CTkEntry(self.input_frame, textvariable=self.cookie_path, placeholder_text="path/to/cookies.txt")
        self.cookie_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
        self.cookie_btn = ctk.CTkButton(self.input_frame, text="Browse", width=80, command=self.browse_cookies)
        self.cookie_btn.grid(row=5, column=2, padx=10, pady=5)

        # Scan Interval
        self.interval_label = ctk.CTkLabel(self.input_frame, text="Scan Interval (Seconds):")
        self.interval_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.interval_var = tk.IntVar(value=120)
        self.interval_entry = ctk.CTkEntry(self.input_frame, textvariable=self.interval_var)
        self.interval_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        # Buttons Frame
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.start_btn = ctk.CTkButton(self.btn_frame, text="Start Restreaming (RTMP)", command=self.toggle_restream, fg_color="green", hover_color="darkgreen")
        self.start_btn.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.preview_btn = ctk.CTkButton(self.btn_frame, text="Open Preview (for Live Studio)", command=self.open_preview, fg_color="purple", hover_color="darkmagenta")
        self.preview_btn.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Status: Ready", text_color="gray")
        self.status_label.grid(row=3, column=0, padx=20, pady=5)

        # Log Window
        self.log_text = ctk.CTkTextbox(self, state="disabled")
        self.log_text.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="nsew")

        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.url_text.delete("1.0", "end")
                    self.url_text.insert("1.0", config.get("urls", ""))
                    self.rtmp_entry.insert(0, config.get("rtmp_url", ""))
                    self.key_entry.insert(0, config.get("stream_key", ""))
                    self.overlay_entry.insert(0, config.get("overlay_text", ""))
                    self.cookie_path.set(config.get("cookie_path", ""))
                    self.interval_var.set(config.get("scan_interval", 120))
                    self.auto_switch_var.set(config.get("auto_switch", False))
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        config = {
            "urls": self.url_text.get("1.0", "end").strip(),
            "rtmp_url": self.rtmp_entry.get().strip(),
            "stream_key": self.key_entry.get().strip(),
            "overlay_text": self.overlay_entry.get().strip(),
            "cookie_path": self.cookie_path.get().strip(),
            "scan_interval": self.interval_var.get(),
            "auto_switch": self.auto_switch_var.get()
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def browse_cookies(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            self.cookie_path.set(filename)

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def toggle_restream(self):
        if self.restreamer and self.restreamer.is_running:
            self.stop_restream()
        else:
            self.start_restream()

    def start_restream(self):
        self.save_config()
        tiktok_urls_raw = self.url_text.get("1.0", "end").strip()
        rtmp_url = self.rtmp_entry.get().strip()
        stream_key = self.key_entry.get().strip()
        cookie_file = self.cookie_path.get().strip()
        auto_switch = self.auto_switch_var.get()
        scan_interval = self.interval_var.get()
        overlay_text = self.overlay_entry.get().strip()

        if not tiktok_urls_raw or not rtmp_url or not stream_key:
            messagebox.showerror("Error", "Please fill in TikTok URLs, RTMP Server, and Stream Key.")
            return

        # Handle multi-line or comma separated
        tiktok_urls = [u.strip() for u in tiktok_urls_raw.replace('\n', ',').split(',') if u.strip()]

        # CLEANUP: Stop existing restreamer before creating a new one
        if self.restreamer:
            self.log("Stopping previous instance...")
            self.restreamer.stop()

        self.restreamer = TikTokRestreamer(
            tiktok_urls, rtmp_url, stream_key, 
            cookie_file if cookie_file else None,
            auto_switch=auto_switch,
            scan_interval=scan_interval,
            overlay_text=overlay_text if overlay_text else None
        )
        
        self.start_btn.configure(text="Stopping...", state="disabled")
        self.status_label.configure(text="Status: Connecting...", text_color="yellow")
        
        # Run in thread
        threading.Thread(target=self._run_restream, daemon=True).start()

    def _run_restream(self):
        self.restreamer.start(self.log)
        
        # Wait a bit to check if it actually started
        if self.restreamer.is_running:
            self.after(0, lambda: self.start_btn.configure(text="Stop Restreaming", state="normal", fg_color="red", hover_color="darkred"))
            self.after(0, lambda: self.status_label.configure(text="Status: Live", text_color="green"))
        else:
            self.after(0, lambda: self.start_btn.configure(text="Start Restreaming", state="normal", fg_color="green", hover_color="darkgreen"))
            self.after(0, lambda: self.status_label.configure(text="Status: Failed", text_color="red"))

    def stop_restream(self):
        if self.restreamer:
            self.log("Stopping restream...")
            self.restreamer.stop()
            self.start_btn.configure(text="Start Restreaming", fg_color="green", hover_color="darkgreen")
            self.status_label.configure(text="Status: Stopped", text_color="gray")

    def open_preview(self):
        self.save_config()
        tiktok_urls_raw = self.url_text.get("1.0", "end").strip()
        if not tiktok_urls_raw:
            messagebox.showerror("Error", "Please enter a TikTok URL first.")
            return

        # Open a preview for each URL in the list
        tiktok_urls = [u.strip() for u in tiktok_urls_raw.replace('\n', ',').split(',') if u.strip()]

        if not self.restreamer:
            # Temporary restreamer for preview
            from tiktok_restreamer import TikTokRestreamer
            self.restreamer = TikTokRestreamer(tiktok_urls, "", "")

        def run_previews():
            for target in tiktok_urls:
                threading.Thread(target=self.restreamer.preview, args=(target, self.log), daemon=True).start()
                import time
                time.sleep(3) # Wait between windows to avoid TikTok blocks

        threading.Thread(target=run_previews, daemon=True).start()

if __name__ == "__main__":
    app = App()
    app.mainloop()
