import tkinter as tk
import random

def update_heart_rate():
    heart_rate = random.randint(60, 100)  # Simulating heart rate in bpm
    heart_rate_label.config(text=f"Your current Heart Rate: {heart_rate} bpm")
    root.after(1000, update_heart_rate)  # Update every second

root = tk.Tk()
root.title("Heart Rate Monitor")
root.geometry("500x400")

heart_rate_label = tk.Label(root, text="Your current heart Rate: -- bpm", font=("Arial", 24))
heart_rate_label.pack(pady=50)

update_heart_rate()  # Start updating heart rate

root.mainloop()