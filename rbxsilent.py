"""
Roblox Window Hider
pip install pywin32 psutil
"""

import win32gui
import win32con
import win32api
import win32process
import ctypes
import time
import threading
import psutil
import os

class RobloxWindowHider:
    def __init__(self):
        self.roblox_windows = {}
        self.show_windows = False
        self.running = True
        self.lock = threading.Lock()
        
        self.scan_interval = 1.0
        self.key_check_interval = 0.05
        self.last_rshift_time = 0
        self.debounce_delay = 0.3
        self.afk_interval = 60
        
        self.user32 = ctypes.windll.user32
        
        try:
            p = psutil.Process(os.getpid())
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        except:
            pass
        
        print("Roblox Window Hider | Right Shift = Toggle | Ctrl+C = Exit")
        print("-" * 55)

    def get_async_key_state(self, vk_code):
        return self.user32.GetAsyncKeyState(vk_code) & 0x8000 != 0

    def enum_callback(self, hwnd, _):
        try:
            if not win32gui.IsWindow(hwnd):
                return True
            if win32gui.GetWindowTextLength(hwnd) == 0:
                return True
            title = win32gui.GetWindowText(hwnd)
            if title == "Roblox":
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    with self.lock:
                        if hwnd not in self.roblox_windows:
                            print(f"[+] Client detected (PID: {pid})")
                        self.roblox_windows[hwnd] = pid
                except:
                    pass
        except:
            pass
        return True

    def scan_windows(self):
        with self.lock:
            old_windows = set(self.roblox_windows.keys())
        
        win32gui.EnumWindows(self.enum_callback, None)
        
        with self.lock:
            current_windows = set(self.roblox_windows.keys())
            for hwnd in old_windows - current_windows:
                print(f"[-] Client closed (HWND: {hwnd})")

    def set_process_priority(self, hwnd, priority):
        try:
            with self.lock:
                pid = self.roblox_windows.get(hwnd)
            if pid:
                handle = win32api.OpenProcess(win32con.PROCESS_SET_INFORMATION, False, pid)
                win32process.SetPriorityClass(handle, priority)
                win32api.CloseHandle(handle)
        except:
            pass

    def hide_window(self, hwnd):
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0)
            self.set_process_priority(hwnd, win32process.IDLE_PRIORITY_CLASS)
        except:
            pass

    def show_window(self, hwnd):
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
            self.set_process_priority(hwnd, win32process.NORMAL_PRIORITY_CLASS)
        except:
            pass

    def toggle_all_windows(self):
        with self.lock:
            windows = list(self.roblox_windows.keys())
        if not windows:
            print("[!] No clients found")
            return
        action = "SHOW" if self.show_windows else "HIDE"
        print(f"[*] {action} {len(windows)} window(s)")
        for hwnd in windows:
            if self.show_windows:
                self.show_window(hwnd)
            else:
                self.hide_window(hwnd)

    def send_afk_input(self):
        """Send space key to all Roblox windows to prevent AFK kick"""
        with self.lock:
            windows = list(self.roblox_windows.keys())
        for hwnd in windows:
            try:
                win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_SPACE, 0)
                time.sleep(0.05)
                win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_SPACE, 0)
            except:
                pass

    def key_monitor_thread(self):
        while self.running:
            if self.get_async_key_state(0xA1):
                current_time = time.time()
                if current_time - self.last_rshift_time > self.debounce_delay:
                    self.show_windows = not self.show_windows
                    self.toggle_all_windows()
                    self.last_rshift_time = current_time
            time.sleep(self.key_check_interval)

    def window_scanner_thread(self):
        while self.running:
            self.scan_windows()
            if not self.show_windows:
                with self.lock:
                    windows = list(self.roblox_windows.keys())
                for hwnd in windows:
                    try:
                        if win32gui.IsWindowVisible(hwnd):
                            self.hide_window(hwnd)
                    except:
                        pass
            time.sleep(self.scan_interval)

    def afk_thread(self):
        """Periodically send space key to prevent AFK kick"""
        while self.running:
            time.sleep(self.afk_interval)
            with self.lock:
                count = len(self.roblox_windows)
            if count > 0:
                self.send_afk_input()
                print(f"[AFK] Sent space to {count} client(s)")

    def run(self):
        print("[*] Scanning for Roblox clients...")
        self.scan_windows()
        
        with self.lock:
            count = len(self.roblox_windows)
        
        if count == 0:
            print("[!] No clients found. Open Roblox first.")
            return
        
        print(f"[+] Found {count} client(s). Monitoring started.\n")
        
        threads = [
            threading.Thread(target=self.key_monitor_thread, daemon=True),
            threading.Thread(target=self.window_scanner_thread, daemon=True),
            threading.Thread(target=self.afk_thread, daemon=True),
        ]
        for t in threads:
            t.start()
        
        try:
            while self.running:
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n[*] Shutting down, restoring windows...")
            self.running = False
            self.show_windows = True
            self.toggle_all_windows()
            time.sleep(0.5)
            print("[✓] Done.")

if __name__ == "__main__":
    try:
        hider = RobloxWindowHider()
        hider.run()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()