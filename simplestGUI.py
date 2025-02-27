import tkinter as tk
import random
import customtkinter as ctk

class HeartRateMonitor:
    def __init__(self):
        # Set appearance mode and default theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title("Heart Rate Monitor")
        
        # Make the window fullscreen
        self.root.attributes('-fullscreen', True)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Create a frame
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Add title label
        self.title_label = ctk.CTkLabel(self.frame, text="Heart Rate Monitor", 
                                        font=ctk.CTkFont(size=36, weight="bold"))
        self.title_label.pack(pady=(40, 60))
        
        # Add heart rate label
        self.heart_rate_label = ctk.CTkLabel(self.frame, text="Your current Heart Rate:", 
                                            font=ctk.CTkFont(size=28))
        self.heart_rate_label.pack(pady=30)
        
        # Add heart rate value display with a larger font
        self.heart_rate_value = ctk.CTkLabel(self.frame, text="--", 
                                           font=ctk.CTkFont(size=120, weight="bold"))
        self.heart_rate_value.pack(pady=20)
        
        # Add bpm label
        self.bpm_label = ctk.CTkLabel(self.frame, text="BPM", 
                                      font=ctk.CTkFont(size=24))
        self.bpm_label.pack(pady=(0, 50))
        
        # Add button frame
        self.button_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.button_frame.pack(pady=40)
        
        # Add Start/Stop button
        self.is_measuring = False
        self.measure_button = ctk.CTkButton(self.button_frame, text="Start Measuring", 
                                           command=self.toggle_measurement,
                                           font=ctk.CTkFont(size=20),
                                           width=300, height=70,
                                           fg_color="#28a745", hover_color="#218838")
        self.measure_button.pack(side="left", padx=20)
        
        # Add Reset button
        self.reset_button = ctk.CTkButton(self.button_frame, text="Reset", 
                                         command=self.reset_monitor,
                                         font=ctk.CTkFont(size=20),
                                         width=200, height=70,
                                         fg_color="#6c757d", hover_color="#5a6268")
        self.reset_button.pack(side="left", padx=20)
        
        # Add Exit button
        self.exit_button = ctk.CTkButton(self.button_frame, text="Exit", 
                                        command=self.exit_application,
                                        font=ctk.CTkFont(size=20),
                                        width=200, height=70,
                                        fg_color="#dc3545", hover_color="#c82333")
        self.exit_button.pack(side="left", padx=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.frame, text="Ready to start", 
                                        font=ctk.CTkFont(size=24))
        self.status_label.pack(pady=30)
        
        # Add keyboard shortcut to exit fullscreen (Escape key)
        self.root.bind("<Escape>", lambda event: self.exit_application())
        
        # Timer ID for updating
        self.update_timer = None
        
    def toggle_measurement(self):
        if not self.is_measuring:
            # Start measuring
            self.is_measuring = True
            self.measure_button.configure(text="Stop Measuring", fg_color="#dc3545", hover_color="#c82333")
            self.status_label.configure(text="Measuring...")
            self.update_heart_rate()
        else:
            # Stop measuring
            self.is_measuring = False
            self.measure_button.configure(text="Start Measuring", fg_color="#28a745", hover_color="#218838")
            self.status_label.configure(text="Paused")
            if self.update_timer:
                self.root.after_cancel(self.update_timer)
                self.update_timer = None
    
    def update_heart_rate(self):
        if self.is_measuring:
            # Simulating heart rate in bpm
            heart_rate = random.randint(60, 100)
            
            # Update heart rate display
            self.heart_rate_value.configure(text=f"{heart_rate}")
            
            # Determine heart rate status and color
            if heart_rate < 60:
                status_text = "Low heart rate"
                status_color = "#17a2b8"  # info blue
            elif heart_rate > 100:
                status_text = "High heart rate"
                status_color = "#dc3545"  # danger red
            else:
                status_text = "Normal heart rate"
                status_color = "#28a745"  # success green
            
            self.status_label.configure(text=status_text, text_color=status_color)
            
            # Schedule next update
            self.update_timer = self.root.after(1000, self.update_heart_rate)
    
    def reset_monitor(self):
        # Reset the display
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None
        
        self.is_measuring = False
        self.heart_rate_value.configure(text="--")
        self.measure_button.configure(text="Start Measuring", fg_color="#28a745", hover_color="#218838")
        self.status_label.configure(text="Ready to start", text_color=("gray10", "gray90"))
    
    def exit_application(self):
        # Exit the application
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HeartRateMonitor()
    app.run()