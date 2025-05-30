import tkinter as tk
import time
import random
import customtkinter as ctk
import time
import pygame
import threading
from heartBeats_new import PulseSensorReader

class HeartRateMonitor:
    def __init__(self):
        # start sensor thread
        self.sensor = PulseSensorReader(channel=0, gain=2/3, buffer_size=10)
        self.sensor.start()

        # Initiate pygame mixer
        pygame.mixer.init()

        # Set appearance mode and theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title("Heart Rate Monitor")
        self.root.after(1000, lambda: self.root.wm_attributes('-fullscreen', 'true'))
        
        # Variables for heart rate tracking
        self.is_measuring = False
        self.current_heart_rate = 0
        self.heart_rate_readings = []
        self.measuring_start_time = 0
        self.measuring_duration = 15  # seconds
        
        # Variables for storing pre- and post-exercise averages
        self.before_activity_avg = None
        self.after_activity_avg = None
        
        # Workflow state:
        # "ready"     : Not started yet ; button to start pre-exercise measurement.
        # "before"    : Currently doing pre-exercise measurement.
        # "between"   : Pre-exercise complete; waiting for music to be played.
        # "after"     : Ready for post-exercise measurement.
        # "completed" : Post-exercise measurement complete.
        self.current_phase = "ready"
        
        # Build the interface
        self.build_interface()
        
        # Timer ID for scheduled tasks
        self.update_timer = None

    def build_interface(self):
        # Main frame
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # --- Top Section: Title and Current Heart Rate ---
        self.top_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=(20, 0))
        self.title_label = ctk.CTkLabel(self.top_frame, text="Heart Rate Monitor", 
                                        font=ctk.CTkFont(size=36, weight="bold"))
        self.title_label.pack(pady=(20, 30))
        
        self.current_hr_frame = ctk.CTkFrame(self.frame)
        self.current_hr_frame.pack(pady=20, fill="x", padx=50)
        self.heart_rate_label = ctk.CTkLabel(self.current_hr_frame, text="Current Heart Rate:", 
                                             font=ctk.CTkFont(size=24))
        self.heart_rate_label.pack(pady=(20, 10))
        self.heart_rate_value = ctk.CTkLabel(self.current_hr_frame, text="--", 
                                             font=ctk.CTkFont(size=80, weight="bold"))
        self.heart_rate_value.pack(pady=5)
        self.bpm_label = ctk.CTkLabel(self.current_hr_frame, text="BPM", 
                                      font=ctk.CTkFont(size=20))
        self.bpm_label.pack(pady=(0, 20))
        self.timer_label = ctk.CTkLabel(self.current_hr_frame, text="Time Remaining: --", 
                                        font=ctk.CTkFont(size=20))
        self.timer_label.pack(pady=(0, 20))
        
        # --- Middle Section: Pre/Post Averages ---
        self.avg_frame = ctk.CTkFrame(self.frame)
        self.avg_frame.pack(pady=20, fill="x", padx=50)
        self.avg_title = ctk.CTkLabel(self.avg_frame, text="Mindfulness Exercises Effectiveness", 
                                      font=ctk.CTkFont(size=24, weight="bold"))
        self.avg_title.pack(pady=(20, 20))
        
        # Create grid for averages and difference
        self.grid_frame = ctk.CTkFrame(self.avg_frame, fg_color="transparent")
        self.grid_frame.pack(pady=(0, 20), fill="x")
        
        # Column for pre-exercise measurement
        self.before_label = ctk.CTkLabel(self.grid_frame, text="BEFORE EXERCISE", 
                                         font=ctk.CTkFont(size=18, weight="bold"))
        self.before_label.grid(row=0, column=0, padx=40, pady=10)
        self.before_avg_value = ctk.CTkLabel(self.grid_frame, text="--", 
                                             font=ctk.CTkFont(size=36, weight="bold"))
        self.before_avg_value.grid(row=1, column=0, padx=40, pady=5)
        self.before_bpm_label = ctk.CTkLabel(self.grid_frame, text="BPM (avg)", 
                                             font=ctk.CTkFont(size=16))
        self.before_bpm_label.grid(row=2, column=0, padx=40, pady=5)
        
        # Column for difference
        self.diff_label = ctk.CTkLabel(self.grid_frame, text="DIFFERENCE", 
                                       font=ctk.CTkFont(size=18, weight="bold"))
        self.diff_label.grid(row=0, column=1, padx=40, pady=10)
        self.diff_value = ctk.CTkLabel(self.grid_frame, text="--", 
                                       font=ctk.CTkFont(size=36, weight="bold"))
        self.diff_value.grid(row=1, column=1, padx=40, pady=5)
        self.diff_bpm_label = ctk.CTkLabel(self.grid_frame, text="BPM", 
                                           font=ctk.CTkFont(size=16))
        self.diff_bpm_label.grid(row=2, column=1, padx=40, pady=5)
        
        # Column for post-exercise measurement
        self.after_label = ctk.CTkLabel(self.grid_frame, text="AFTER EXERCISE", 
                                        font=ctk.CTkFont(size=18, weight="bold"))
        self.after_label.grid(row=0, column=2, padx=40, pady=10)
        self.after_avg_value = ctk.CTkLabel(self.grid_frame, text="--", 
                                           font=ctk.CTkFont(size=36, weight="bold"))
        self.after_avg_value.grid(row=1, column=2, padx=40, pady=5)
        self.after_bpm_label = ctk.CTkLabel(self.grid_frame, text="BPM (avg)", 
                                           font=ctk.CTkFont(size=16))
        self.after_bpm_label.grid(row=2, column=2, padx=40, pady=5)
        
        # Configure grid columns equally
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)
        self.grid_frame.grid_columnconfigure(2, weight=1)
        
        # Status label (for instructions)
        self.status_label = ctk.CTkLabel(self.avg_frame, text="Ready to start measurement", 
                                         font=ctk.CTkFont(size=18))
        self.status_label.pack(pady=(0, 20))
        
        # --- Bottom Section: Main Control Button and Others ---
        self.button_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.button_frame.pack(pady=30, fill="x")
        
        # Single main button that changes function based on phase
        self.measure_button = ctk.CTkButton(self.button_frame, 
                                            text="Start Pre-exercise Measurement",
                                            command=self.start_next_phase,
                                            font=ctk.CTkFont(size=20),
                                            width=400, height=70,
                                            fg_color="#28a745", hover_color="#218838")
        self.measure_button.pack(side="top", pady=10)
        
        # Additional control buttons: Reset and Exit - removed in this version
        # self.bottom_buttons = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        # self.bottom_buttons.pack(pady=10)
        # self.reset_button = ctk.CTkButton(self.bottom_buttons, text="Reset All", 
        #                                   command=self.reset_monitor,
        #                                   font=ctk.CTkFont(size=20),
        #                                   width=200, height=70,
        #                                   fg_color="#6c757d", hover_color="#5a6268")
        # self.reset_button.pack(side="left", padx=20)
        # self.exit_button = ctk.CTkButton(self.bottom_buttons, text="Exit", 
        #                                  command=self.exit_application,
        #                                  font=ctk.CTkFont(size=20),
        #                                  width=200, height=70,
        #                                  fg_color="#dc3545", hover_color="#c82333")
        # self.exit_button.pack(side="left", padx=20)
        
        # Allow pressing Escape to exit fullscreen
        self.root.bind("<Escape>", lambda event: self.exit_application())

    def start_next_phase(self):
        if self.current_phase == "ready":
            # Start pre-exercise measurement; change state to "before"
            self.current_phase = "before"
            self.start_measurement("Before Mindfullness Exercises")
            self.measure_button.configure(text="Measuring Heart Rate Before Mindfullness Exercises...", state="disabled")
            self.status_label.configure(text="Measuring resting heart rate before mindfulness exercises...")
        elif self.current_phase == "between":
            # In the between phase, button now plays music.
            self.play_music_and_wait()
        elif self.current_phase == "after":
            # Start post-exercise measurement.
            self.start_measurement("After Mindfullness Exercises")
            self.measure_button.configure(text="Measuring Heart Rate After Mindfullness Exercises...", state="disabled")
            self.status_label.configure(text="Measuring heart rate after mindfulness exercises...")

    def start_measurement(self, phase_name):
        # Reset readings and start measurement
        self.heart_rate_readings = []
        self.measuring_start_time = time.time()
        self.is_measuring = True
        self.update_heart_rate()

    def update_heart_rate(self):
        if self.is_measuring:
            elapsed_time = time.time() - self.measuring_start_time
            remaining_time = max(0, self.measuring_duration - elapsed_time)
            self.timer_label.configure(text=f"Time Remaining: {int(remaining_time)} sec")
            
            # Simulated heart rate: slightly lower range after exercise if in after phase.
            self.current_heart_rate = int(self.sensor.bpm)
            
            # Printing the current heart rate for debugging
            print(self.current_heart_rate)
            
            # Update the heart rate value and append to readings
            self.heart_rate_readings.append(self.current_heart_rate)
            self.heart_rate_value.configure(text=f"{self.current_heart_rate}")
            
            # Update text color based on heart rate value
            if self.current_heart_rate < 60:
                status_color = "#17a2b8"  # blue
            elif self.current_heart_rate > 100:
                status_color = "#dc3545"  # red
            else:
                status_color = "#28a745"  # green
            self.heart_rate_value.configure(text_color=status_color)
            
            if elapsed_time >= self.measuring_duration:
                self.complete_measurement()
            else:
                self.update_timer = self.root.after(200, self.update_heart_rate)

    def complete_measurement(self):
        self.is_measuring = False
        if self.heart_rate_readings:
            avg_heart_rate = sum(self.heart_rate_readings) / len(self.heart_rate_readings)
        else:
            avg_heart_rate = 0

        if self.current_phase == "before":
            # Save pre-exercise average and update state.
            self.before_activity_avg = avg_heart_rate
            self.before_avg_value.configure(text=f"{int(avg_heart_rate)}")
            self.current_phase = "between"
            self.status_label.configure(text="Pre-exercise measurement complete. Click the button to play mindfulness exercises.")
            self.measure_button.configure(text="Play Mindfulness Exercises", state="normal", fg_color="#17a2b8", hover_color="#138496")
        elif self.current_phase == "after":
            # Save post-exercise average and display the difference.
            self.after_activity_avg = avg_heart_rate
            self.after_avg_value.configure(text=f"{int(avg_heart_rate)}")
            diff = int(self.after_activity_avg - self.before_activity_avg)
            self.diff_value.configure(text=f"{'+' if diff > 0 else ''}{diff}")
            if diff > 0:
                self.diff_value.configure(text_color="#dc3545")
            elif diff < 0:
                self.diff_value.configure(text_color="#28a745")
            else:
                self.diff_value.configure(text_color=("gray10", "gray90"))
            # Replace the main button with a Reset button for convenience.
            self.current_phase = "completed"
            self.status_label.configure(text="Post-exercise measurement complete! Click the Reset button to start again.")
            self.measure_button.configure(text="Reset", state="normal", command=self.reset_monitor,
                                          fg_color="#6c757d", hover_color="#5a6268")

    def play_music_and_wait(self):
        try:
            pygame.mixer.music.load("roar.mp3")
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()
            self.status_label.configure(text="Playing midfulness exercises...")
            self.measure_button.configure(state="disabled")
            self.check_music_status()  # Start checking for when music finishes.
        except Exception as e:
            self.status_label.configure(text=f"Error playing mindfulness exercises: {e}")

    def check_music_status(self):
        if pygame.mixer.music.get_busy():
            self.root.after(1000, self.check_music_status)
        else:
            # Music has finished; update button for post-exercise measurement.
            self.current_phase = "after"
            self.status_label.configure(text="Mindfulness exercises are finished. Click the button to start post-exercise measurement.")
            self.measure_button.configure(text="Start Post-exercise Measurement", state="normal",
                                          command=self.start_next_phase,
                                          fg_color="#28a745", hover_color="#218838")

    def reset_monitor(self):
        # Cancel any pending update timers.
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None
        pygame.mixer.music.stop()
        self.is_measuring = False
        self.heart_rate_readings = []
        self.current_phase = "ready"
        self.before_activity_avg = None
        self.after_activity_avg = None
        self.heart_rate_value.configure(text="--", text_color=("gray10", "gray90"))
        self.before_avg_value.configure(text="--")
        self.after_avg_value.configure(text="--")
        self.diff_value.configure(text="--", text_color=("gray10", "gray90"))
        self.timer_label.configure(text="Time Remaining: --")
        self.measure_button.configure(text="Start Pre-exercise Measurement", state="normal",
                                      fg_color="#28a745", hover_color="#218838", command=self.start_next_phase)
        self.status_label.configure(text="Ready to start measurement")

    def exit_application(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HeartRateMonitor()
    app.run()
