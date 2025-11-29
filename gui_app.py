import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import threading


class EMRAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Heidi - EMR Automation")
        self.root.geometry("380x450")
        self.root.resizable(False, False)  # Fixed size - no resizing
        
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.selected_profile = tk.StringVar(value="")
        self.listener = None
        self.is_listening = False
        self.animating = False
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # Setup ttk styles
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Helvetica", 11))
        
        self.build_ui()
    
    def build_ui(self):
        # Header using ttk labels (works with macOS dark/light mode)
        ttk.Label(self.root, text="Automate your admin with Heidi!", style="Title.TLabel").pack(pady=(20, 5))
        ttk.Label(self.root, text="Streamline your clinical documentation", style="Subtitle.TLabel").pack(pady=(0, 15))
        
        # Download button
        self.download_btn = tk.Button(
            self.root,
            text="Download Profiles",
            command=self.download_profiles,
            font=("Helvetica", 11),
            width=18
        )
        self.download_btn.pack(pady=5)
        
        self.download_status = tk.Label(self.root, text="", font=("Helvetica", 10))
        self.download_status.pack()
        
        # Profile selection
        tk.Label(self.root, text="Available EMR Profiles:", font=("Helvetica", 11)).pack(pady=(15, 5))
        
        # Scrollable frame for profiles
        self.profile_container = tk.Frame(self.root)
        self.profile_container.pack(fill="both", expand=True, padx=20)
        
        self.canvas = tk.Canvas(self.profile_container, height=120, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.profile_container, orient="vertical", command=self.canvas.yview)
        self.radio_frame = tk.Frame(self.canvas)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.radio_frame, anchor="nw")
        
        self.radio_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.refresh_profiles()
        
        # Start button
        self.start_btn = tk.Button(
            self.root,
            text="Start Listening",
            command=self.start_listening,
            font=("Helvetica", 11)
        )
        self.start_btn.pack(pady=15)
        
        # Status
        self.status_label = tk.Label(self.root, text="", font=("Helvetica", 10))
        self.status_label.pack()
        
        # Exit
        tk.Button(self.root, text="Exit", command=self.on_exit).pack(side="bottom", pady=10)
    
    def download_profiles(self):
        self.download_btn.config(state="disabled", text="Loading...")
        self.download_status.config(text="")
        self.animating = True
        self.dot_count = 0
        self.animate_loading()
        
        def run():
            try:
                subprocess.run(
                    [sys.executable, os.path.join(self.script_dir, "download_profiles.py")],
                    cwd=self.script_dir,
                    capture_output=True
                )
                self.root.after(0, self.download_complete)
            except:
                self.root.after(0, self.download_failed)
        
        threading.Thread(target=run, daemon=True).start()
    
    def animate_loading(self):
        if not self.animating:
            return
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count if self.dot_count > 0 else ""
        self.download_btn.config(text=f"Loading{dots}")
        self.root.after(300, self.animate_loading)
    
    def download_complete(self):
        self.animating = False
        self.download_btn.config(state="normal", text="Download Profiles")
        self.download_status.config(text="✓ Profiles downloaded")
        self.refresh_profiles()
    
    def download_failed(self):
        self.animating = False
        self.download_btn.config(state="normal", text="Download Profiles")
        self.download_status.config(text="✗ Download failed")
    
    def refresh_profiles(self):
        for w in self.radio_frame.winfo_children():
            w.destroy()
        
        profiles = self.get_profiles()
        
        if not profiles:
            tk.Label(self.radio_frame, text="No profiles found", fg="gray").pack()
        else:
            self.selected_profile.set("")  # Clear selection first
            for p in profiles:
                rb = tk.Radiobutton(
                    self.radio_frame,
                    text=p,
                    value=p,
                    variable=self.selected_profile,
                    font=("Helvetica", 11),
                    indicatoron=True,
                    selectcolor="#4a90d9"
                )
                rb.pack(anchor="w")
            self.selected_profile.set(profiles[0])
    
    def get_profiles(self):
        profiles_dir = os.path.join(self.script_dir, "emr_profiles")
        if not os.path.exists(profiles_dir):
            return []
        
        profiles = []
        for item in os.listdir(profiles_dir):
            config = os.path.join(profiles_dir, item, "config.json")
            if os.path.isdir(os.path.join(profiles_dir, item)) and os.path.exists(config):
                profiles.append(item)
        return sorted(profiles)
    
    def start_listening(self):
        profile = self.selected_profile.get()
        if not profile:
            self.status_label.config(text="Select a profile first")
            return
        
        if self.is_listening:
            return
        
        self.is_listening = True
        self.start_btn.config(state="disabled")
        self.status_label.config(text=f"Press Cmd+Shift+K to run '{profile}'")
        
        # Start global hotkey listener
        threading.Thread(target=self.run_global_hotkey_listener, daemon=True).start()
    
    def run_global_hotkey_listener(self):
        from Quartz import (
            CGEventMaskBit, kCGEventKeyDown, CGEventGetIntegerValueField,
            kCGKeyboardEventKeycode, CGEventGetFlags,
            kCGEventFlagMaskShift, kCGEventFlagMaskCommand
        )
        from Quartz.CoreGraphics import CGEventTapCreate, CGEventTapEnable
        from Quartz.CoreGraphics import kCGHeadInsertEventTap, kCGEventTapOptionDefault, kCGSessionEventTap
        import Quartz
        from Foundation import NSRunLoop, NSDate
        
        # Key code for 'K' is 40
        K_KEYCODE = 40
        
        def callback(proxy, event_type, event, refcon):
            if event_type == kCGEventKeyDown:
                keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
                flags = CGEventGetFlags(event)
                
                cmd_pressed = (flags & kCGEventFlagMaskCommand) != 0
                shift_pressed = (flags & kCGEventFlagMaskShift) != 0
                
                if keycode == K_KEYCODE and cmd_pressed and shift_pressed:
                    if self.is_listening:
                        self.root.after(0, lambda: threading.Thread(target=self.run_automation, daemon=True).start())
            
            return event
        
        event_mask = CGEventMaskBit(kCGEventKeyDown)
        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            kCGEventTapOptionDefault,
            event_mask,
            callback,
            None
        )
        
        if tap is None:
            self.root.after(0, lambda: self.status_label.config(text="Error: Enable Accessibility permissions"))
            return
        
        run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
        Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), run_loop_source, Quartz.kCFRunLoopCommonModes)
        CGEventTapEnable(tap, True)
        
        # Run loop to keep listening
        while self.is_listening:
            NSRunLoop.currentRunLoop().runMode_beforeDate_(Quartz.kCFRunLoopDefaultMode, NSDate.dateWithTimeIntervalSinceNow_(0.1))
    
    def run_automation(self):
        profile = self.selected_profile.get()
        self.root.after(0, lambda: self.status_label.config(text=f"Running {profile}..."))
        
        try:
            from main import run_sequence_from_config
            config_path = os.path.join(self.script_dir, "emr_profiles", profile, "config.json")
            run_sequence_from_config(config_path)
            self.root.after(0, lambda: self.status_label.config(text="Done! Press Cmd+Shift+K again"))
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Error: {e}"))
    
    def on_exit(self):
        self.is_listening = False
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    EMRAutomationApp(root)
    root.mainloop()
