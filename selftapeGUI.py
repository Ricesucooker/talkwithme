import sys
import os
import time
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from audio_manager import audioManager
import re
 
class SelfTapeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎙️TalkWithMe app")
        self.geometry("800x600")
        self.config(bg="#f0f0f0")
        
        # Logic
        self.audio_manager = None
        try:
            self.audio_manager = audioManager()
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))
            self.destroy()
            return

        self.is_running = False
        self.audition_thread = None
        self.recorded_takes = []
        self.script_lines = []
        self.character_roles = []
        self.my_character = ""

        self.create_widgets()

    # Building GUI Layout 
    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#f0f0f0", padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Script Area 
        tk.Label(main_frame, text="Enter your script here:").pack(pady=(0,5))
        self.script_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=25, width=100)
        self.script_text.pack(pady=5)
        self.script_text.bind("<<Modified>>", self.update_character_list)
        self.script_text.insert(tk.END, """
                                Sophie: Honestly, what a mess this place is. One would think a powerful wizard could keep things tidy.
                                Howl: Tidy? My dear, a chaotic artist needs chaos to create! Besides, what would I do without my dear, sweet cleaning lady to take care of everything?
                                Sophie: Sweet indeed. He's as flighty as a butterfly and twice as vain.
                                Howl: But you, my dear seem so weary.Are you sure you're up to this? You're not some ancient crone, are you? 
                                """)
        self.script_text.edit_modified(False)

        # Buttons and Options
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10)

        tk.Label(control_frame, text="Your Character:").pack(side=tk.LEFT, padx=(0,5))
        self.character_var = tk.StringVar(control_frame)
        self.character_dropdown = ttk.Combobox(control_frame, textvariable=self.character_var, state="readonly")
        self.character_dropdown.pack(side=tk.LEFT, padx=(0,20))

        self.start_button = tk.Button(control_frame, text="Start Audition 🎬", command=self.start_audition, bg="#28a745", fg="white", font=("Helvetica", 12, "bold"))
        self.start_button.pack(side=tk.LEFT, padx=(0,5))
        
        self.playback_button = tk.Button(control_frame, text="Playback Take", command=self.play_full_take, state="disabled", bg="#007bff", fg="white", font=("Helvetica", 12, "bold"))
        self.playback_button.pack(side=tk.LEFT, padx=(5,5))

        self.stop_button = tk.Button(control_frame, text="Stop", command=self.stop_audition, state=tk.DISABLED, bg="#dc3545", fg="white", font=("Helvetica", 12, "bold"))
        self.stop_button.pack(side=tk.LEFT, padx=(5,0))

        # Status 
        self.status_label = tk.Label(main_frame, text="Ready to begin.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
    
        self.update_character_list()
    
    # Character Parsing
    def update_character_list(self, event=None):
        script_content = self.script_text.get("1.0", tk.END)
 
        characters = re.findall(r'^\s*([A-Z][a-zA-Z\s\.]*):\s*', script_content, re.MULTILINE)

        if characters:
            unique_characters = sorted(list(set(c.strip() for c in characters)))
            self.character_roles = unique_characters
            self.character_dropdown['values'] = unique_characters
            if self.character_var.get() not in unique_characters:
                self.character_var.set(unique_characters[0])
        else:
            self.character_roles = []
            self.character_dropdown['values'] = []
            self.character_var.set("No characters found.")

        self.script_text.edit_modified(False)

    def parse_script(self, script_content):
        lines = script_content.strip().split('\n')
        parsed_script = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match = re.match(r'\s*([A-Z][a-zA-Z\s\.]*):\s*(.*)', line)
            if match:
                character = match.group(1).strip()
                dialogue = match.group(2).strip()
                if dialogue:
                    parsed_script.append((character, dialogue))
        return parsed_script

    # Main Audition Logic
    def start_audition(self):
        script_content = self.script_text.get("1.0", tk.END)
        if not script_content.strip():
            self.update_status("Please enter a script.")
            return
        
        self.my_character = self.character_var.get()
        if self.my_character not in self.character_roles:
            self.update_status("Please select a valid character.")
            return

        self.script_lines = self.parse_script(script_content)
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.playback_button.config(state=tk.DISABLED)
        self.script_text.config(state=tk.DISABLED)
        self.character_dropdown.config(state=tk.DISABLED)
        
        self.update_status("Audition started ...")

        self.audition_thread = threading.Thread(target=self._run_audition)
        self.audition_thread.daemon = True
        self.audition_thread.start()

    def _run_audition(self):
        try:
            take_number = 1 
            self.recorded_takes = []
            self.audio_manager.is_running = True

            for character, line in self.script_lines:
                if not self.is_running:
                    break
                
                if character == self.my_character:
                    self.update_status(f"YOUR LINE: {line}")
                    filename = f"take_{take_number}.wav"
                    recorded_file = self.audio_manager.record_audio_until_silence(filename)

                    if os.path.exists(recorded_file) and os.path.getsize(recorded_file) > 1000:
                        self.recorded_takes.append(recorded_file)
                        take_number += 1
                    else:
                        self.update_status("Recording failed or was too short. Skipping.")
                else:
                    self.update_status(f"{character}: {line}")
                    self.audio_manager.speak(line)
            
            if self.is_running:
                self.update_status("Audition finished. You can now play back your take.")
                self.playback_button.config(state=tk.NORMAL)
        except Exception as e:
            self.update_status(f"An error occurred: {e}")
            messagebox.showerror("Error", f'An error occurred during audition: {e}')
        finally:
            self.stop_audition_cleanup()
    
    def play_full_take(self):
        """Plays back the full take, interleaving recorded audio with TTS."""
        if self.is_running or not self.recorded_takes:
            return
        
        self.update_status("Playing back full take...")
        
        take_index = 0
        for character, line in self.script_lines:
            if character == self.my_character:
                if take_index < len(self.recorded_takes):
                    filename = self.recorded_takes[take_index]
                    self.audio_manager.play_audio_file(filename)
                    take_index += 1
            else:
                self.audio_manager.speak(line)
        
        self.update_status("Playback finished.")

    def stop_audition(self):
        self.is_running = False
        self.update_status("Audition stopped.")

    def stop_audition_cleanup(self):
        self.is_running = False
        self.audio_manager.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.script_text.config(state=tk.NORMAL)
        self.character_dropdown.config(state="readonly")
        
    def update_status(self, message):
        self.after(0, lambda: self.status_label.config(text=message))
    
    def on_quit(self):
        self.is_running = False
        if self.audition_thread and self.audition_thread.is_alive():
            self.audition_thread.join()
        if self.audio_manager:
            self.audio_manager.shutdown()
        self.destroy()

if __name__ == "__main__":
    app = SelfTapeApp()
    app.mainloop()
