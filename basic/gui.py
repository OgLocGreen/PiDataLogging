# temperature_gui.py

import tkinter as tk
from tkinter import ttk
import subprocess
import json
from datetime import datetime, timedelta
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

class TemperatureApp:
    def __init__(self, master):
        self.master = master
        master.title("Temperaturmessung Steuerung")

        self.current_date = datetime.now()
        self.show_date = self.current_date
        self.temperature_data = []
        self.data_values = []
        self.data_timestamps = []
        self.process_humidity_air = None
        self.process_temperatur = None
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # Erstellen von Frames für die Organisation
        self.top_frame = tk.Frame(master)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.bottom_frame = tk.Frame(master)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.left_frame = tk.Frame(self.top_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.top_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Widgets im linken Frame (Logs)
        self.label = ttk.Label(self.left_frame, text=self.current_date.strftime('%Y-%m-%d'))
        self.label.pack()

        self.text = tk.Text(self.left_frame, height=10, width=50)
        self.text.pack()

        # Widgets im rechten Frame (Graph)
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        # Erstellen von vier Plots innerhalb der Figur
        self.plots = {
            1: self.figure.add_subplot(2, 2, 1),
            2: self.figure.add_subplot(2, 2, 2),
            3: self.figure.add_subplot(2, 2, 3),
            4: self.figure.add_subplot(2, 2, 4)
        }

        self.canvas = FigureCanvasTkAgg(self.figure, self.right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Widgets im bottom Frame (Navigation)
        self.prev_button = ttk.Button(self.bottom_frame, text="Vorheriger Tag", command=self.prev_day)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.start_button = tk.Button(self.bottom_frame, text="Messung Starten", command=self.start_measurement, fg="red")
        self.start_button.pack(side=tk.BOTTOM, padx=5, pady=5)

        self.next_button = ttk.Button(self.bottom_frame, text="Nächster Tag", command=self.next_day)
        self.next_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.load_data(self.current_date)

    def load_data(self, date):
        base_path = os.path.join(self.script_dir, "logging_data")
        file_name = f"{base_path}/temperatur_log_{date.strftime('%Y-%m-%d')}.json"
        self.temperature_data = []
        try:
            with open(file_name, "r") as file:
                self.temperature_data = json.load(file)
                print("Daten geladen")
        except FileNotFoundError:
                print("Keine Daten vorhanden")
                pass
        self.update_display(date)

    def load_week_data(self, start_date):
        week_data = []  # Eine Liste, die für jeden Tag eine Liste von stündlichen Durchschnittswerten enthält
        for i in range(7):
            day = start_date + timedelta(days=i)
            file_name = f"{self.script_dir}/logging_data/temperatur_log_{day.strftime('%Y-%m-%d')}.json"
            daily_data = []
            try:
                with open(file_name, "r") as file:
                    data = json.load(file)
                    for hour in range(24):
                        hourly_data = [entry['average_temperature'] for entry in data if datetime.strptime(entry['time'], '%Y-%m-%d %H:%M:%S').hour == hour]
                        if hourly_data:
                            daily_data.append(sum(hourly_data) / len(hourly_data))
                        else:
                            daily_data.append(None)  # Keine Daten für diese Stunde
            except FileNotFoundError:
                daily_data = [None] * 24  # Keine Daten für diesen Tag
            week_data.append(daily_data)
        return week_data

    def update_week_graph(self, plot_pos, week_data):
        plot = self.plots[plot_pos]  # Zugriff auf den entsprechenden Plot basierend auf plot_pos
        plot.clear()  # Vorheriges Diagramm löschen

        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        for i, daily_data in enumerate(week_data):
            if daily_data:
                hours = range(24)
                plot.plot(hours, daily_data, label=days[i % 7])
        
        plot.set_title('Wöchentliche Durchschnittstemperatur')
        plot.set_xlabel('Stunde')
        plot.set_ylabel('Temperatur (°C)')
        plot.legend()

        self.canvas.draw()
   

    def update_graph(self,plot_pos, date, dates, temperatures):
        # Löschen des aktuellen Inhalts des Plots
        plot = self.plots[plot_pos]
        self.text.delete(1.0, tk.END)
        plot.clear()
        if len(dates) == 0 or len(temperatures) == 0:
            self.canvas.draw()
            return
        else:
            self.label.config(text=date.strftime('%Y-%m-%d'))         
            # Übergeben der Daten an den Plot
            plot.plot(temperatures, label='Temperatur')
            
            plot.set_title('Durchschnittstemperatur')
            plot.set_ylabel('Temperatur (°C)')
            plot.legend()
            
            # Zeichnen des aktualisierten Plots
            self.canvas.draw()

    def update_log(self, dates, temperatures):
        if len(dates) == 0 or len(temperatures) == 0:
            self.text.insert(tk.END, "Keine Daten vorhanden\n")
        for timestamp, temperature in zip(dates, temperatures):
            self.text.insert(tk.END, f"{timestamp}: {temperature}°C\n")

    def update_display(self, date):
        self.text.delete(1.0, tk.END)  # Löscht den aktuellen Inhalt des Text-Widgets
        self.label.config(text=date)  # Aktualisiert das Label mit dem aktuellen Datum
        
        self.data_values = []
        self.data_timestamps = []
        try:
            for entry in self.temperature_data:
                # Fügt jeden Eintrag in das Text-Widget ein
                self.text.insert(tk.END, f"{entry['time']}: {entry['average_temperature']}°C\n")
                self.data_values.append(entry['average_temperature'])
                self.data_timestamps.append(entry['time'])
        except:
            print("Fehler beim Laden der Daten")
            pass
        self.update_graph(3, self.show_date, self.data_timestamps, self.data_values)
        self.update_log(self.data_timestamps, self.data_values)
        
    def prev_day(self):
        self.show_date -= timedelta(days=1)
        self.load_data(self.show_date)

    def next_day(self):
        self.show_date += timedelta(days=1)
        self.load_data(self.show_date)

    def start_measurement(self):
            if self.process_temperatur is None and self.process_humidity_air is None:
                # Starte das Temperaturmessungs-Skript als separaten Prozess
                self.process_temperatur = subprocess.Popen(['python', f'{self.script_dir}/temperature_logger.py'])
                self.process_humidity_air = subprocess.Popen(['python', f'{self.script_dir}/humidity_air_logger.py'])
                
                self.start_button.config(text="Messung Stoppen", fg="green", command=self.stop_measurement)
            else:
                self.stop_measurement()

    def stop_measurement(self):
        if self.process_temperatur is not None:
            self.process_temperatur.terminate()
            self.process_temperatur = None
        self.start_button.config(text="Messung Starten", fg="red", command=self.start_measurement)


if __name__ == "__main__":
    root = tk.Tk()
    app = TemperatureApp(root)
    root.mainloop()
