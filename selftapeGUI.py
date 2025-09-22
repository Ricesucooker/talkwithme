import sys 
import os
import time
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from audio_manager import audioManager

class SelfTapeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎙️TalkWithMe app")
        self.geometry("800x600")
        self.config(bg="#f0f0f0")

        self.audio_manager = None
        try:
            self.audio_manager = audioManager()
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))
            self.destroy()
            return
        self.is_running = False
        self.audition_thread = None

        self.recorded_take = []
        self.full_script_line = []
        self.my_character = None

        self.create_widgets()

    #building gui layout
    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#f0f0f0", padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        script_frame = tk.LabelFrame(main_frame, text="Eneter Script", bg="white", padx=10, pady=10)
        script_frame.pack(fill="both", expand=True, pady=10)

        self.script_text = scrolledtext.ScrolledText(script_frame, wrap=tk.WORD, width=60, height=15, font=("helvetico",12))
        self.script_text.pack(fill="both", expand=True, pady=10)
        self.script_text.insert(tk.END, """Sophie: Honestly, what a mess this place is. One would think a powerful wizard could keep things tidy.
                                Howl: Tidy? My dear, a chaotic artist needs chaos to create! Besides, what would I do without my dear, sweet cleaning lady to take care of everything?
                                Sophie: Sweet indeed. He's as flighty as a butterfly and twice as vain.
                                Howl: But you, my dear seem so weary.Are you sure you're up to this? You're not some ancient crone, are you? """) 
        

        controls_frame = tk.Frame(main_frame, bg="#f0f0f0")
        controls_frame.pack(fill="x", pady=10)
        
        # Character selection
        tk.Label(controls_frame, text="Your Character:", bg="#f0f0f0", font=("Helvetica", 12, "bold")).pack(side="left", padx=(0, 5))
        self.character_var = tk.StringVar()
        self.character_dropdown = ttk.Combobox(controls_frame, textvariable=self.character_var, state="readonly")
        self.character_dropdown.pack(side="left", padx=(0, 20))
        
        # Buttons
        self.start_button = tk.Button(controls_frame, text="Start Audition", command=self.start_audition, bg="#28a745", fg="white", font=("Helvetica", 12, "bold"), relief="raised")
        self.start_button.pack(side="left", padx=5, ipadx=10, ipady=5)
        
        self.playback_button = tk.Button(controls_frame, text="Playback Take", command=self.play_full_take, state="disabled", bg="#007bff", fg="white", font=("Helvetica", 12, "bold"), relief="raised")
        self.playback_button.pack(side="left", padx=5, ipadx=10, ipady=5)
        
        self.quit_button = tk.Button(controls_frame, text="Quit", command=self.on_quit, bg="#dc3545", fg="white", font=("Helvetica", 12, "bold"), relief="raised")
        self.quit_button.pack(side="left", padx=5, ipadx=10, ipady=5)
        
        #  Status Display
        self.status_label = tk.Label(main_frame, text="Ready.", font=("Helvetica", 14), bg="#f0f0f0", relief="sunken", anchor="w")
        self.status_label.pack(fill="x", pady=10, ipady=5)
        
        self.update_character_list()
        self.script_text.bind("<<Modified>>", self.on_script_modified)

    def on_script_modified(self, event=None):
        self.update_character_list()
        self.script_text.edit_modified(False)
    
    def update_character_list(self):
        script_text = self.script_text.get("1.0", tk.END)
        parsed_script = self.parse_script(script_text)
        characters = sorted(list(set(line[0] for line in parsed_script)))
        self.character_dropdown['values'] = characters
        if self.character_var.get() not in characters:
            self.character_var.set(characters[0] if characters else "")
    
    def parse_script(self, script_text):
        lines = script_text.strip().split('\n')
        parsed_line = []
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                character = parts[0].strip().upper()
                dialogue = parts[1].strip()
                parsed_line.append((character, dialogue))
        return parsed_line
    
    def start_audition(self):
        if self.is_running:
            return
        self.my_character = self.character_var.get()
        if not self.my_character:
            messagebox.showwarning("Warning","Please Select a character.")
            return
        self.is_running = True
        self.start_button.config(state="disabled")
        self.playback_button.config(state="disabled")
        self.script_text.config(state="disabled")
        self.character_dropdown.config(state="disabled")
        self.status_label.config(text="In progress....")

        self.recorded_take = []
        script_text = self.script_text.get("1.0", tk.END)
        self.full_script_line = self.parse_script(script_text)

        self.audition_thread = threading.Thread(target=self._run_audition)
        self.audition_thread.daemon = True
        self.audition_thread.start()

    def _run_audition(self):
        try:
            self.status_label.config(text="Starting...")
            time.sleep(1)
            self.audio_manager.is_running = True

            for character, line in self.script:
                if not self.is_running:
                    break

                if character == self.my_character:
                    self.status_label.config(text=f"YOUR LINE: {line}")
                    filename = f"take_{i+1}.wav"
                    self.audio_manager.record_audio_until_silence(filename)
                    self.recorded_take.append(filename)
                else:
                    self.status_label.config(text=f"{character} : {line}")
                    self.audio_manager.speak(line)
            self.status_label.config(text= "Audition finished. You can now play back your take! 📹")
            self.playback_button.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during recording: {e}")
        finally:
            self.is_running =False
            self.start_button.config(state="normal")
            self.script_text.config(state="normal")
            self.character_dropdown.config(state="readonly")
            self.audio_manager.is_running = False
        
    def play_full_take(self):
        if self.is_running or not self.recorded_take:
            return
        self.status_label.config(text="PLaying back full take ...")

        take_idex = 0
        for character, line in self.full_script_line:
            if character == self.my_character:
                if take_idex < len(self.recorded_take):
                    filename = self.recorded_take[take_idex]
                    self.audio_manager.play_audio_file(filename)
                    take_idex +=1
                else:
                    self.audio_manager.speak("take missing from this line")
            else:
                self.audio_manager.speak(line)
        self.status_label.config(text="Playback finnished.")
    
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