import subprocess
import threading
import os
import time
import random

class TikTokRestreamer:
    def __init__(self, tiktok_urls, rtmp_url, stream_key, cookie_path=None, auto_switch=False, scan_interval=120, overlay_text=None):
        # tiktok_urls can be a list or a single string
        if isinstance(tiktok_urls, str):
            self.tiktok_urls = [url.strip() for url in tiktok_urls.split(',') if url.strip()]
        else:
            self.tiktok_urls = tiktok_urls
            
        self.rtmp_url = rtmp_url
        self.stream_key = stream_key
        self.cookie_path = cookie_path
        self.auto_switch = auto_switch
        self.scan_interval = scan_interval # Default wait between full scans
        self.overlay_text = overlay_text
        self.process = None
        self.is_running = False
        self.stop_event = threading.Event()
        self.current_target = None

    def get_stream_url(self, url):
        """Extracts the direct stream URL from a specific TikTok URL with best quality."""
        command = ['yt-dlp', '-f', 'best', '-g', url]
        if self.cookie_path and os.path.exists(self.cookie_path):
            command.extend(['--cookies', self.cookie_path])
        
        try:
            # Add some common headers to avoid bot detection
            command.extend(['--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'])
            
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return None
        except Exception:
            return None

    def start(self, log_callback):
        """Starts the restreaming process (with auto-switch support)."""
        self.stop_event.clear()
        self.is_running = True
        threading.Thread(target=self._main_loop, args=(log_callback,), daemon=True).start()

    def _main_loop(self, log_callback):
        while self.is_running and not self.stop_event.is_set():
            target_found = False
            for url in self.tiktok_urls:
                if self.stop_event.is_set(): break
                
                log_callback(f"Checking status for: {url}...")
                stream_url = self.get_stream_url(url)
                
                if stream_url:
                    log_callback(f"Found Live! Starting restream for {url}...")
                    self.current_target = url
                    self._run_ffmpeg(stream_url, log_callback)
                    target_found = True
                    if not self.auto_switch:
                        self.is_running = False
                        return
                    log_callback("Live ended. Searching for next target...")
                    break 
                
                # Add a random delay between checking different accounts to look human
                inter_check_delay = random.uniform(5, 15)
                for _ in range(int(inter_check_delay)):
                    if self.stop_event.is_set(): break
                    threading.Event().wait(1)
                
            if not target_found:
                if not self.auto_switch:
                    log_callback("No live streams found in the list.")
                    self.is_running = False
                    return
                
                # Randomized wait interval to avoid bot detection
                wait_time = self.scan_interval + random.randint(-30, 30)
                wait_time = max(30, wait_time) # Minimum 30s
                
                log_callback(f"No one is live. Waiting {wait_time} seconds before next full scan...")
                for _ in range(wait_time):
                    if self.stop_event.is_set(): break
                    threading.Event().wait(1)

        self.is_running = False
        log_callback("Auto-Switch system stopped.")

    def _run_ffmpeg(self, stream_url, log_callback):
        """Internal method to run FFmpeg and wait for it."""
        try:
            full_rtmp_url = f"{self.rtmp_url}/{self.stream_key}"
            # (RTMP URL joining logic remains same)
            if not self.rtmp_url.endswith('/') and not self.stream_key.startswith('/'):
                full_rtmp_url = f"{self.rtmp_url}/{self.stream_key}"
            elif self.rtmp_url.endswith('/') and self.stream_key.startswith('/'):
                full_rtmp_url = f"{self.rtmp_url}{self.stream_key[1:]}"

            command = ['ffmpeg', '-re', '-i', stream_url]
            
            if self.overlay_text:
                # Need to re-encode for filters
                # FFmpeg path escaping for Windows fontfile: C\:/Windows/Fonts/...
                font_path = "C\\:/Windows/Fonts/arial.ttf"
                filter_str = f"drawtext=text='{self.overlay_text}':fontfile='{font_path}':fontcolor=white:fontsize=28:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-100"
                
                command.extend([
                    '-c:v', 'libx264',
                    '-preset', 'superfast',
                    '-crf', '23', 
                    '-maxrate', '2500k',
                    '-bufsize', '5000k',
                    '-pix_fmt', 'yuv420p',
                    '-g', '50', # Better for live sync
                    '-vf', filter_str,
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-f', 'flv',
                    full_rtmp_url
                ])
            else:
                command.extend([
                    '-c', 'copy',
                    '-f', 'flv',
                    full_rtmp_url
                ])

            self.process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                text=True, bufsize=1, universal_newlines=True
            )
            
            for line in self.process.stdout:
                if self.stop_event.is_set(): break
                log_callback(line.strip())
            
            self.process.wait()
        except Exception as e:
            log_callback(f"FFmpeg Error: {str(e)}")
        finally:
            if self.process:
                self.process.terminate()
            self.process = None
            self.current_target = None

    def stop(self):
        """Stops the restreaming process."""
        self.stop_event.set()
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.is_running = False

    def _parse_cookies_for_ffmpeg(self):
        """Parses Netscape cookies.txt and returns a string for FFmpeg headers."""
        if not self.cookie_path or not os.path.exists(self.cookie_path):
            return ""
        
        cookies = []
        try:
            with open(self.cookie_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) >= 7:
                        name = parts[5]
                        value = parts[6]
                        cookies.append(f"{name}={value}")
            return "; ".join(cookies)
        except Exception:
            return ""

    def preview(self, url, log_callback):
        """Opens a preview window using robust binary piping."""
        try:
            log_callback(f"Starting robust piped preview for {url}...")
            
            # 1. Command for yt-dlp to output raw data to stdout
            ytdlp_cmd = [
                'yt-dlp', 
                '--quiet', '--no-warnings', 
                '-f', 'best', 
                '-o', '-', 
                url
            ]
            if self.cookie_path and os.path.exists(self.cookie_path):
                ytdlp_cmd.extend(['--cookies', self.cookie_path])
            
            # 2. Command for ffplay to read from stdin (pipe:0)
            ffplay_cmd = [
                'ffplay', 
                '-i', 'pipe:0', 
                '-alwaysontop', 
                '-window_title', f"Preview - {url}",
                '-x', '400', '-y', '711', 
                '-loglevel', 'error'
            ]
            
            if self.overlay_text:
                font_path = "C\\:/Windows/Fonts/arial.ttf"
                filter_str = f"drawtext=text='{self.overlay_text}':fontfile='{font_path}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-80"
                ffplay_cmd.extend(['-vf', filter_str])

            # Start yt-dlp and redirect stderr to null to avoid polluting stdout
            ytdlp_proc = subprocess.Popen(
                ytdlp_cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.DEVNULL,
                bufsize=10**6 # Large buffer for smooth streaming
            )
            
            # Start ffplay reading from yt-dlp's stdout
            subprocess.Popen(ffplay_cmd, stdin=ytdlp_proc.stdout)
            
            log_callback("Piped preview started. If the shop is LIVE, the window will appear shortly.")
        except Exception as e:
            log_callback(f"Preview Error: {str(e)}")
