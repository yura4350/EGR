import tkinter as tk
import random
import customtkinter as ctk
import time
import pygame
from datetime import datetime

class HeartRateMonitor:
    def __init__(self):

        #initiating pygame mixer
        pygame.mixer.init()

        # Set appearance mode and default theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title("Heart Rate Monitor")
        
        # Make the window fullscreen
        self.root.after(1000, lambda: self.root.wm_attributes('-fullscreen', 'true'))
        
        # Variables for heart rate tracking
        self.is_measuring = False
        self.current_heart_rate = 0
        self.heart_rate_readings = []
        self.measuring_start_time = 0
        self.measuring_duration = 15  # 30 seconds for average calculation
        
        # Variables for activity comparison
        self.before_activity_avg = None
        self.after_activity_avg = None
        self.current_phase = "ready"  # Possible values: ready, before, between, after, completed
        
        # Create a main frame
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Top section - Title and current reading
        self.top_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        # Add title label
        self.title_label = ctk.CTkLabel(self.top_frame, text="Heart Rate Monitor", 
                                        font=ctk.CTkFont(size=36, weight="bold"))
        self.title_label.pack(pady=(20, 30))
        
        # Current heart rate display
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
        
        # Timer label
        self.timer_label = ctk.CTkLabel(self.current_hr_frame, text="Time Remaining: --", 
                                      font=ctk.CTkFont(size=20))
        self.timer_label.pack(pady=(0, 20))
        
        # Middle section - Averages display
        self.avg_frame = ctk.CTkFrame(self.frame)
        self.avg_frame.pack(pady=20, fill="x", padx=50)
        
        self.avg_title = ctk.CTkLabel(self.avg_frame, text="Mindfullness Exercises Effectiveness", 
                                     font=ctk.CTkFont(size=24, weight="bold"))
        self.avg_title.pack(pady=(20, 20))
        
        # Create a grid for before/after averages
        self.grid_frame = ctk.CTkFrame(self.avg_frame, fg_color="transparent")
        self.grid_frame.pack(pady=(0, 20), fill="x")
        
        # Before Mindfullness Exercises column
        self.before_label = ctk.CTkLabel(self.grid_frame, text="BEFORE EXERCISE", 
                                        font=ctk.CTkFont(size=18, weight="bold"))
        self.before_label.grid(row=0, column=0, padx=40, pady=10)
        
        self.before_avg_value = ctk.CTkLabel(self.grid_frame, text="--", 
                                           font=ctk.CTkFont(size=36, weight="bold"))
        self.before_avg_value.grid(row=1, column=0, padx=40, pady=5)
        
        self.before_bpm_label = ctk.CTkLabel(self.grid_frame, text="BPM (avg)", 
                                           font=ctk.CTkFont(size=16))
        self.before_bpm_label.grid(row=2, column=0, padx=40, pady=5)
        
        # Difference column
        self.diff_label = ctk.CTkLabel(self.grid_frame, text="DIFFERENCE", 
                                      font=ctk.CTkFont(size=18, weight="bold"))
        self.diff_label.grid(row=0, column=1, padx=40, pady=10)
        
        self.diff_value = ctk.CTkLabel(self.grid_frame, text="--", 
                                     font=ctk.CTkFont(size=36, weight="bold"))
        self.diff_value.grid(row=1, column=1, padx=40, pady=5)
        
        self.diff_bpm_label = ctk.CTkLabel(self.grid_frame, text="BPM", 
                                         font=ctk.CTkFont(size=16))
        self.diff_bpm_label.grid(row=2, column=1, padx=40, pady=5)
        
        # After Mindfullness Exercises column
        self.after_label = ctk.CTkLabel(self.grid_frame, text="AFTER EXERCISE", 
                                       font=ctk.CTkFont(size=18, weight="bold"))
        self.after_label.grid(row=0, column=2, padx=40, pady=10)
        
        self.after_avg_value = ctk.CTkLabel(self.grid_frame, text="--", 
                                          font=ctk.CTkFont(size=36, weight="bold"))
        self.after_avg_value.grid(row=1, column=2, padx=40, pady=5)
        
        self.after_bpm_label = ctk.CTkLabel(self.grid_frame, text="BPM (avg)", 
                                          font=ctk.CTkFont(size=16))
        self.after_bpm_label.grid(row=2, column=2, padx=40, pady=5)
        
        # Configure grid columns to be equal width
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)
        self.grid_frame.grid_columnconfigure(2, weight=1)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.avg_frame, text="Ready to start measurement", 
                                        font=ctk.CTkFont(size=18))
        self.status_label.pack(pady=(0, 20))
        
        # Bottom section - Control buttons
        self.button_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.button_frame.pack(pady=30, fill="x")
        
        # Start measuring button
        self.measure_button = ctk.CTkButton(self.button_frame, text="Start Pre-exercise Measurement", 
                                           command=self.start_next_phase,
                                           font=ctk.CTkFont(size=20),
                                           width=400, height=70,
                                           fg_color="#28a745", hover_color="#218838")
        self.measure_button.pack(side="top", pady=10)
        
        # Bottom row buttons
        self.bottom_buttons = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        self.bottom_buttons.pack(pady=10)
        
        # Reset button
        self.reset_button = ctk.CTkButton(self.bottom_buttons, text="Reset All", 
                                         command=self.reset_monitor,
                                         font=ctk.CTkFont(size=20),
                                         width=200, height=70,
                                         fg_color="#6c757d", hover_color="#5a6268")
        self.reset_button.pack(side="left", padx=20)

        # Music button
        # Play Music button
        self.music_button = ctk.CTkButton(self.bottom_buttons, text="Play Music",
                                          command=self.play_music,
                                          font=ctk.CTkFont(size=20),
                                          width=200, height=70,
                                          fg_color="#17a2b8", hover_color="#138496")
        
        self.music_button.pack(side="left", padx=20)

        # Exit button
        self.exit_button = ctk.CTkButton(self.bottom_buttons, text="Exit", 
                                        command=self.exit_application,
                                        font=ctk.CTkFont(size=20),
                                        width=200, height=70,
                                        fg_color="#dc3545", hover_color="#c82333")
        self.exit_button.pack(side="left", padx=20)
        
        # Add keyboard shortcut to exit fullscreen (Escape key)
        self.root.bind("<Escape>", lambda event: self.exit_application())
        
        # Timer ID for updating
        self.update_timer = None
        
    def play_music(self):
        try:
            pygame.mixer.music.load("Frank Ocean - Miss You So.mp3")
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()
            self.status_label.configure(text="Playing music: Frank Ocean - Miss You So 🎵")
        except Exception as e:
            self.status_label.configure(text=f"Error playing music: {e}")
    
    def show_music_window(self):
        music_window = ctk.CTkToplevel(self.root)
        music_window.title("Mindfulness Music")
        music_window.geometry("400x200")
        music_window.grab_set()

        label = ctk.CTkLabel(music_window, text="Click below to play calming music",
                            font=ctk.CTkFont(size=18))
        label.pack(pady=20)

        play_button = ctk.CTkButton(music_window, text="Play Music",
                                    command=self.play_music,
                                    font=ctk.CTkFont(size=20),
                                    fg_color="#17a2b8", hover_color="#138496")
        play_button.pack(pady=10)

        # Optional: Close button
        close_button = ctk.CTkButton(music_window, text="Close",
                                    command=music_window.destroy,
                                    font=ctk.CTkFont(size=16),
                                    fg_color="#6c757d", hover_color="#5a6268")
        close_button.pack(pady=10)

    def start_next_phase(self):
        if self.current_phase == "ready":
            # Start the "before mindfullness exercises" measurement
            self.current_phase = "before"
            self.start_measurement("Before Mindfullness Exercises")
            self.measure_button.configure(text="Measuring Heart Rate Before Mindfullness Exercises...", state="disabled")
            self.status_label.configure(text="Measuring resting heart rate before mindfullness exercises...")
            
        elif self.current_phase == "between":
            # Start the "after mindfullness exercises" measurement
            self.current_phase = "after"
            self.start_measurement("After Mindfullness Exercises")
            self.measure_button.configure(text="Measuring Heart Rate After Mindfullness Exercises...", state="disabled")
            self.status_label.configure(text="Measuring heart rate after mindfullness exercises...")
            
    def start_measurement(self, phase_name):
        # Reset readings for this phase
        self.heart_rate_readings = []
        self.measuring_start_time = time.time()
        self.is_measuring = True
        
        # Start updating heart rate
        self.update_heart_rate()
    
    def update_heart_rate(self):
        if self.is_measuring:
            # Calculate elapsed time
            elapsed_time = time.time() - self.measuring_start_time
            remaining_time = max(0, self.measuring_duration - elapsed_time)
            
            # Update timer display
            self.timer_label.configure(text=f"Time Remaining: {int(remaining_time)} sec")
            
            # Simulating heart rate in bpm - in a real application, this would come from a sensor
            if self.current_phase == "after":
                # Simulate slightly elevated heart rate after mindfullness exercises
                self.current_heart_rate = random.randint(60, 100)
            else:
                self.current_heart_rate = random.randint(75, 115)
            
            # Add reading to our list
            self.heart_rate_readings.append(self.current_heart_rate)
            
            # Update heart rate display
            self.heart_rate_value.configure(text=f"{self.current_heart_rate}")
            
            # Determine heart rate status and color
            if self.current_heart_rate < 60:
                status_color = "#17a2b8"  # info blue
            elif self.current_heart_rate > 100:
                status_color = "#dc3545"  # danger red
            else:
                status_color = "#28a745"  # success green
            
            self.heart_rate_value.configure(text_color=status_color)
            
            # Check if measurement period is complete
            if elapsed_time >= self.measuring_duration:
                self.complete_measurement()
            else:
                # Schedule next update
                self.update_timer = self.root.after(1000, self.update_heart_rate)
    
    def complete_measurement(self):
        self.is_measuring = False

        if len(self.heart_rate_readings) > 0:
            avg_heart_rate = sum(self.heart_rate_readings) / len(self.heart_rate_readings)
        else:
            avg_heart_rate = 0

        if self.current_phase == "before":
            self.before_activity_avg = avg_heart_rate
            self.before_avg_value.configure(text=f"{int(avg_heart_rate)}")

            # Move to "between" phase
            self.current_phase = "between"
            self.status_label.configure(text="Now perform your mindfulness exercise. Play music if desired.")
            self.measure_button.configure(text="Start After-exercise Measurement",
                                        state="normal",
                                        fg_color="#007bff",
                                        hover_color="#0069d9")

            self.show_music_window()

        elif self.current_phase == "after":
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

            self.current_phase = "completed"
            self.measure_button.configure(text="Measurement Complete", state="disabled")
            self.status_label.configure(text="Measurement complete! Press 'Reset All' to start a new comparison.")

    
    def reset_monitor(self):
        # Cancel any pending updates
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None
        
        # Reset all variables
        self.is_measuring = False
        self.heart_rate_readings = []
        self.current_phase = "ready"
        self.before_activity_avg = None
        self.after_activity_avg = None
        
        # Reset displays
        self.heart_rate_value.configure(text="--", text_color=("gray10", "gray90"))
        self.before_avg_value.configure(text="--")
        self.after_avg_value.configure(text="--")
        self.diff_value.configure(text="--", text_color=("gray10", "gray90"))
        self.timer_label.configure(text="Time Remaining: --")
        
        # Reset button and status
        self.measure_button.configure(text="Start Before Mindfullness Exercise Measurement", 
                                    state="normal", 
                                    fg_color="#28a745", 
                                    hover_color="#218838")
        self.status_label.configure(text="Ready to start measurement")
    
    def exit_application(self):
        # Exit the application
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HeartRateMonitor()
    app.run()