import time
import customtkinter as ctk
import pygame
from sensor_reader import PulseSensorReader

class HeartRateMonitorApp:
    def __init__(self):
        # Start the pulse sensor reader thread
        self.sensor = PulseSensorReader(channel=0, gain=2/3, buffer_size=10)
        self.sensor.start()

        # Initialize pygame mixer for music playback
        pygame.mixer.init()

        # CTkinter setup
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.root.title("Heart Rate Monitor")
        # Enter fullscreen after a brief delay
        self.root.after(1000, lambda: self.root.wm_attributes('-fullscreen', 'true'))

        # State variables
        self.current_phase = "ready"
        self.heart_rate_readings = []
        self.measuring_start_time = 0
        self.measuring_duration = 15  # seconds
        self.before_activity_avg = None
        self.after_activity_avg = None
        self.update_timer = None

        # Build the UI
        self.build_interface()

        # Ensure clean shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)

    def build_interface(self):
        # Main container
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Top: Title and current heart rate
        self.top_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=(20, 0))
        self.title_label = ctk.CTkLabel(
            self.top_frame,
            text="Heart Rate Monitor",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        self.title_label.pack(pady=(20, 30))

        self.current_hr_frame = ctk.CTkFrame(self.frame)
        self.current_hr_frame.pack(pady=20, fill="x", padx=50)
        self.heart_rate_label = ctk.CTkLabel(
            self.current_hr_frame,
            text="Current Heart Rate:",
            font=ctk.CTkFont(size=24)
        )
        self.heart_rate_label.pack(pady=(20, 10))
        self.heart_rate_value = ctk.CTkLabel(
            self.current_hr_frame,
            text="--",
            font=ctk.CTkFont(size=80, weight="bold")
        )
        self.heart_rate_value.pack(pady=5)
        self.bpm_label = ctk.CTkLabel(
            self.current_hr_frame,
            text="BPM",
            font=ctk.CTkFont(size=20)
        )
        self.bpm_label.pack(pady=(0, 20))
        self.timer_label = ctk.CTkLabel(
            self.current_hr_frame,
            text="Time Remaining: --",
            font=ctk.CTkFont(size=20)
        )
        self.timer_label.pack(pady=(0, 20))

        # Middle: Pre/post averages
        self.avg_frame = ctk.CTkFrame(self.frame)
        self.avg_frame.pack(pady=20, fill="x", padx=50)
        self.avg_title = ctk.CTkLabel(
            self.avg_frame,
            text="Mindfulness Exercises Effectiveness",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.avg_title.pack(pady=(20, 20))

        self.grid_frame = ctk.CTkFrame(self.avg_frame, fg_color="transparent")
        self.grid_frame.pack(pady=(0, 20), fill="x")
        # BEFORE column
        self.before_label = ctk.CTkLabel(
            self.grid_frame,
            text="BEFORE EXERCISE",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.before_label.grid(row=0, column=0, padx=40, pady=10)
        self.before_avg_value = ctk.CTkLabel(
            self.grid_frame,
            text="--",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        self.before_avg_value.grid(row=1, column=0, padx=40, pady=5)
        self.before_bpm_label = ctk.CTkLabel(
            self.grid_frame,
            text="BPM (avg)",
            font=ctk.CTkFont(size=16)
        )
        self.before_bpm_label.grid(row=2, column=0, padx=40, pady=5)
        # DIFFERENCE column
        self.diff_label = ctk.CTkLabel(
            self.grid_frame,
            text="DIFFERENCE",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.diff_label.grid(row=0, column=1, padx=40, pady=10)
        self.diff_value = ctk.CTkLabel(
            self.grid_frame,
            text="--",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        self.diff_value.grid(row=1, column=1, padx=40, pady=5)
        self.diff_bpm_label = ctk.CTkLabel(
            self.grid_frame,
            text="BPM",
            font=ctk.CTkFont(size=16)
        )
        self.diff_bpm_label.grid(row=2, column=1, padx=40, pady=5)
        # AFTER column
        self.after_label = ctk.CTkLabel(
            self.grid_frame,
            text="AFTER EXERCISE",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.after_label.grid(row=0, column=2, padx=40, pady=10)
        self.after_avg_value = ctk.CTkLabel(
            self.grid_frame,
            text="--",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        self.after_avg_value.grid(row=1, column=2, padx=40, pady=5)
        self.after_bpm_label = ctk.CTkLabel(
            self.grid_frame,
            text="BPM (avg)",
            font=ctk.CTkFont(size=16)
        )
        self.after_bpm_label.grid(row=2, column=2, padx=40, pady=5)
        # equal columns
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)
        self.grid_frame.grid_columnconfigure(2, weight=1)

        # status/instructions
        self.status_label = ctk.CTkLabel(
            self.avg_frame,
            text="Ready to start measurement",
            font=ctk.CTkFont(size=18)
        )
        self.status_label.pack(pady=(0, 20))

        # Bottom: controls
        self.button_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.button_frame.pack(pady=30, fill="x")
        self.measure_button = ctk.CTkButton(
            self.button_frame,
            text="Start Pre-exercise Measurement",
            command=self.start_next_phase,
            font=ctk.CTkFont(size=20),
            width=400,
            height=70,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.measure_button.pack(side="top", pady=10)

        self.bottom_buttons = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        self.bottom_buttons.pack(pady=10)
        self.reset_button = ctk.CTkButton(
            self.bottom_buttons,
            text="Reset All",
            command=self.reset_monitor,
            font=ctk.CTkFont(size=20),
            width=200,
            height=70,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        self.reset_button.pack(side="left", padx=20)
        self.exit_button = ctk.CTkButton(
            self.bottom_buttons,
            text="Exit",
            command=self.exit_application,
            font=ctk.CTkFont(size=20),
            width=200,
            height=70,
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.exit_button.pack(side="left", padx=20)
        self.root.bind("<Escape>", lambda e: self.exit_application())

    def start_next_phase(self):
        if self.current_phase == "ready":
            self.current_phase = "before"
            self.start_measurement()
            self.measure_button.configure(
                text="Measuring Heart Rate Before Mindfulness...",
                state="disabled"
            )
            self.status_label.configure(text="Measuring resting heart rate before mindfulness exercises...")
        elif self.current_phase == "between":
            self.play_music_and_wait()
        elif self.current_phase == "after":
            self.start_measurement()
            self.measure_button.configure(
                text="Measuring Heart Rate After Mindfulness...",
                state="disabled"
            )
            self.status_label.configure(text="Measuring heart rate after mindfulness exercises...")

    def start_measurement(self):
        self.heart_rate_readings = []
        self.measuring_start_time = time.time()
        self.update_heart_rate()

    def update_heart_rate(self):
        elapsed = time.time() - self.measuring_start_time
        remaining = max(0, self.measuring_duration - elapsed)
        self.timer_label.configure(text=f"Time Remaining: {int(remaining)} sec")

        # Pull the latest BPM from the sensor
        bpm = int(self.sensor.bpm)
        self.heart_rate_readings.append(bpm)
        self.heart_rate_value.configure(text=str(bpm))

        # Color coding
        if bpm < 60:
            color = "#17a2b8"
        elif bpm > 100:
            color = "#dc3545"
        else:
            color = "#28a745"
        self.heart_rate_value.configure(text_color=color)

        if elapsed >= self.measuring_duration:
            self.complete_measurement()
        else:
            self.update_timer = self.root.after(1000, self.update_heart_rate)

    def complete_measurement(self):
        avg = sum(self.heart_rate_readings) / len(self.heart_rate_readings) if self.heart_rate_readings else 0
        if self.current_phase == "before":
            self.before_activity_avg = avg
            self.before_avg_value.configure(text=str(int(avg)))
            self.current_phase = "between"
            self.status_label.configure(text="Pre-exercise measurement complete. Click to play music.")
            self.measure_button.configure(
                text="Play Music",
                state="normal",
                fg_color="#17a2b8",
                hover_color="#138496"
            )
        elif self.current_phase == "after":
            self.after_activity_avg = avg
            self.after_avg_value.configure(text=str(int(avg)))
            diff = int(self.after_activity_avg - self.before_activity_avg)
            sign = "+" if diff > 0 else ""
            self.diff_value.configure(text=f"{sign}{diff}")
            # color diff
            if diff > 0:
                diff_color = "#dc3545"
            elif diff < 0:
                diff_color = "#28a745"
            else:
                diff_color = "gray10"
            self.diff_value.configure(text_color=diff_color)
            self.current_phase = "completed"
            self.status_label.configure(text="Post-exercise complete! Click Reset to start again.")
            self.measure_button.configure(
                text="Reset",
                state="normal",
                command=self.reset_monitor,
                fg_color="#6c757d",
                hover_color="#5a6268"
            )

    def play_music_and_wait(self):
        try:
            pygame.mixer.music.load("roar.mp3")
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()
            self.status_label.configure(text="Playing calming music...")
            self.measure_button.configure(state="disabled")
            self.root.after(1000, self.check_music_status)
        except Exception as e:
            self.status_label.configure(text=f"Error playing music: {e}")

    def check_music_status(self):
        if pygame.mixer.music.get_busy():
            self.root.after(1000, self.check_music_status)
        else:
            self.current_phase = "after"
            self.status_label.configure(text="Music finished. Click to start post-exercise measurement.")
            self.measure_button.configure(
                text="Start Post-exercise Measurement",
                state="normal",
                command=self.start_next_phase,
                fg_color="#28a745",
                hover_color="#218838"
            )

    def reset_monitor(self):
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None
        pygame.mixer.music.stop()
        self.current_phase = "ready"
        self.heart_rate_readings = []
        self.before_activity_avg = None
        self.after_activity_avg = None
        self.heart_rate_value.configure(text="--", text_color="gray10")
        self.before_avg_value.configure(text="--")
        self.diff_value.configure(text="--", text_color="gray10")
        self.after_avg_value.configure(text="--")
        self.timer_label.configure(text="Time Remaining: --")
        self.measure_button.configure(
            text="Start Pre-exercise Measurement",
            command=self.start_next_phase,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.status_label.configure(text="Ready to start measurement")

    def exit_application(self):
        self.cleanup()

    def cleanup(self):
        # Stop sensor thread
        self.sensor.stop()
        self.sensor.join()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HeartRateMonitorApp()
    app.run()
