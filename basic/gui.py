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


LABEL_SIZE = 8
TITLE_SIZE = 10

class LoggingApp:
    def __init__(self, master):
        self.master = master
        master.title("PiLogging")

        self.current_date = datetime.now()
        self.show_date = self.current_date
        
        self.temperature_data_day = []
        self.temperature_data_week = []
        self.humidity_data_day = []
        self.humidity_data_week = []

        self.timestamps_day = []
        self.timestamps_week = []

        self.sensor_type = ['temperature', 'humidity']

        # Overview data
        self.temp_ahora = 0
        self.temp_day = 0
        self.temp_week = 0
        self.humi_ahora = 0
        self.humi_day = 0
        self.humi_week = 0

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

        # Erstellen des Frames für den unteren Teil des linken Frames
        self.left_bottom_frame = tk.Frame(self.left_frame)
        self.left_bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


        self.right_frame = tk.Frame(self.top_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Widgets im links oben Frame (Logs) 
        self.label = ttk.Label(self.left_frame, text=self.show_date.strftime('%Y-%m-%d'))
        self.label.pack()

        self.log_text = tk.Text(self.left_frame, height=10, width=50)
        self.log_text.pack()

        # Widget links Mitting
        data_overview = ttk.Label(self.left_bottom_frame, text="Data Overview")
        data_overview.pack()

        self.overview_temp = tk.Label(self.left_bottom_frame, text= ("Temp: " +  str(self.temp_ahora) + " AvgTempDay: "+   str(self.temp_day) + " AvgTempWeek:" +   str(self.temp_week)))
        self.overview_temp.pack()

        self.overview_humi = tk.Label(self.left_bottom_frame, text= ("Humi: " +   str(self.humi_ahora) + " AvgHumiDay: "+   str(self.humi_day) + " AvgHumiWeek:" +   str(self.humi_week)))
        self.overview_humi.pack()

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

        # Init Data
        self.load_data_day(self.current_date)
        self.load_data_week(self.current_date)
        self.update_display()

    def update_overview(self):
        self.overview_temp.config(text= ("Temp: " +  str(round(self.temp_ahora,2)) + "   AvgTempDay: "+   str(round(self.temp_day,2)) + "   AvgTempWeek:" +   str(round(self.temp_week,2))))
        self.overview_humi.config(text= ("Humi: " +   str(round(self.humi_ahora,2)) + "   AvgHumiDay: "+   str(round(self.humi_day,2)) + "   AvgHumiWeek:" +   str(round(self.humi_week,2))))
        self.overview_humi.pack()

    def load_data_day(self, date):
        base_path = os.path.join(self.script_dir, "logging_data")

        # Laden von Temperatur- und Feuchtigkeitsdaten
        for sensor_type in self.sensor_type:
            file_name = f"{base_path}\\{sensor_type}_log_{date.strftime('%Y-%m-%d')}.json"
            temp_data_day = []
            try:
                with open(file_name, "r") as file:
                    temp_data_day = json.load(file)
                    print("Daten geladen")
            except FileNotFoundError:
                print(f"Keine Daten vorhanden {sensor_type}_data_day")
                continue  # Weiter zum nächsten Sensor-Typ, wenn keine Daten gefunden wurden

            # Extrahieren und Speichern der Daten
            for entry in temp_data_day:
                if sensor_type == 'temperature':
                    self.temperature_data_day.append(entry[f'average_{sensor_type}'])
                elif sensor_type == 'humidity':
                    self.humidity_data_day.append(entry[f'average_{sensor_type}'])
                self.timestamps_day.append(entry['time'])

        self.temp_ahora = self.temperature_data_day[-1]
        self.temp_day = sum(self.temperature_data_day)/ len(self.temperature_data_day)

        self.humi_ahora =  self.humidity_data_day[-1]
        self.humi_day = sum(self.humidity_data_day)/ len(self.humidity_data_day)


    def load_data_week(self, start_date):
        for sensor_type in self.sensor_type:
            sensor_data_week = []
            for i in range(7):
                day = start_date + timedelta(days=i)
                file_name = f"{self.script_dir}/logging_data/{sensor_type}_log_{day.strftime('%Y-%m-%d')}.json"
                daily_data = []
                try:
                    with open(file_name, "r") as file:
                        data = json.load(file)
                        for hour in range(24):
                            hourly_data = [entry[f'average_{sensor_type}'] for entry in data if datetime.strptime(entry['time'], '%Y-%m-%d %H:%M:%S').hour == hour]
                            if hourly_data:
                                daily_data.append(sum(hourly_data) / len(hourly_data))
                            else:
                                daily_data.append(None)  # Keine Daten für diese Stunde
                except FileNotFoundError:
                    daily_data = [None] * 24  # Keine Daten für diesen Tag
                    print(f"Keine Daten vorhanden für {sensor_type}_data_week am {day}")
                sensor_data_week.append(daily_data)
            # Extrahieren und Speichern der Daten
            if sensor_type == 'temperature':
                self.temperature_data_week = []
            elif sensor_type == 'humidity':
                self.humidity_data_week = []

            for entry in sensor_data_week:
                if sensor_type == 'temperature':
                    self.temperature_data_week.append(entry)
                elif sensor_type == 'humidity':
                    self.humidity_data_week.append(entry)


    def update_graph_week(self, plot_pos, week_data, label):
        plot = self.plots[plot_pos]  # Zugriff auf den entsprechenden Plot basierend auf plot_pos
        if plot == 1 or plot == 3:
            return
        
        plot.clear()  # Vorheriges Diagramm löschen

        days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        average = []
        for i, daily_data in enumerate(week_data):
            # Filtern Sie nur die Floats und berechnen Sie dann die Summe und die Anzahl der Floats
            floats = [wert for wert in daily_data if isinstance(wert, float)]
            summe = sum(floats)
            anzahl_floats = len(floats)
            # Berechne den Durchschnitt, falls es Floats gibt, sonst gebe None aus
            average.append( summe / anzahl_floats if anzahl_floats > 0 else 99)

        filtered_data = [wert for wert in average if wert is not None]
        filtered_days = [day for day, wert in zip(days, average) if wert is not None]

        # Erstellen Sie den Plot
        plot.plot(filtered_days, filtered_data)
        # Beschriftungen und Titel hinzufügen
        plot.set_title("Average " + label + " Week")
        # Verkleinern der Beschriftungen
        plot.tick_params(axis='both', labelsize=LABEL_SIZE)
        plot.set_title("Average " + label + " Week", fontsize=TITLE_SIZE) 
        self.canvas.draw()
   

    def update_graph_day(self,plot_pos, values, label):
        # Löschen des aktuellen Inhalts des Plots
        plot = self.plots[plot_pos]
        plot.clear()
        if len(values) == 0:
            self.canvas.draw()
            return
        else:      
            # Übergeben der Daten an den Plot
            plot.plot(values, label=label)
            plot.set_title('Durchschnitts'+label)
            plot.set_ylabel(label)
            plot.tick_params(axis='both', labelsize=LABEL_SIZE)
            plot.set_title("Average " + label + " Week", fontsize=TITLE_SIZE) 
           
            # Zeichnen des aktualisierten Plots
            self.canvas.draw()

    def update_log(self, dates, values):
        if len(dates) == 0 or len(values) == 0:
            self.log_text.insert(tk.END, "Keine Daten vorhanden\n")
        for timestamp, temperature in zip(dates, values):
            self.log_text.insert(tk.END, f"{timestamp}: {temperature}°C\n")


    def update_display(self):
        self.label.config(text=self.show_date.strftime('%Y-%m-%d')) # Aktualisiert das Label mit dem aktuellen Datum
        # Temperature
        self.update_graph_day(1, self.temperature_data_day, "temperature")
        self.update_log(self.timestamps_day, self.temperature_data_day)
        self.update_graph_week(2, self.temperature_data_week, "temperature")

        # Humidity
        self.update_graph_day(3, self.humidity_data_day, "humidity")
        self.update_graph_week(4, self.humidity_data_week, "humidity")

        self.update_overview()

        
    def prev_day(self):
        self.show_date -= timedelta(days=1)
        self.load_data_day(self.show_date)
        self.load_data_week(self.show_date)
        self.update_display()

    def next_day(self):
        self.show_date += timedelta(days=1)
        self.load_data_day(self.show_date)
        self.load_data_week(self.show_date)
        self.update_display()

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
    app = LoggingApp(root)
    root.mainloop()
