import psutil
import time
import json
import random
import os
from datetime import datetime

def get_cpu_temperature():
    # Gibt die CPU-Temperatur zurück. Funktioniert nur unter Linux.
    temps = psutil.sensors_temperatures()
    if 'coretemp' in temps:
        return temps['coretemp'][0].current
    return None

def get_cpu_temperature_2():
    # Gibt die CPU-Temperatur zurück. Funktioniert nur unter Linux.
    temps = psutil.sensors_temperatures()
    if 'coretemp' in temps:
        for entry in temps['coretemp']:
            if entry.label.startswith('Package'):
                return entry.current
    return None

def log_humidity(interval_seconds=1, log_interval=60):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(script_dir, "logging_data")
    os.makedirs(base_path, exist_ok=True)

    current_day = datetime.now().strftime('%Y-%m-%d')
    file_name = os.path.join(base_path, f"humidity_log_{current_day}.json")
    
    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            try:
                log_entry_old = json.load(file)
            except json.JSONDecodeError:
                log_entry_old = []
    else:
        log_entry_old = []

    measurements = []
    start_time = time.time()
    
    while True:
        now = datetime.now()
        new_day = now.strftime('%Y-%m-%d')
        if new_day != current_day:
            # Ein neuer Tag hat begonnen, aktualisiere den Dateinamen und leere die alte Eintragsliste
            current_day = new_day
            file_name = os.path.join(base_path, f"humidity_log_{current_day}.json")
            log_entry_old = []

        try :
            temp = get_cpu_temperature()
        except Exception as e:
            print(f"Fehler beim Auslesen der Temperatur: {e}")
            temp = random.randint(40, 45)
            
        if temp is not None:
            measurements.append(temp)
            print(f"Aktuelle CPU-Temperatur: {temp}°C")

        # Prüfe, ob es Zeit ist, den Mittelwert zu loggen
        if time.time() - start_time >= log_interval:
            if measurements:
                avg_temp = sum(measurements) / len(measurements)
                log_entry = {
                    "time": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "average_humidity": avg_temp
                }
                log_entry_old.append(log_entry)
                
                # Schreibe die aktualisierten Daten in die Datei
                with open(file_name, "w") as file:
                    json.dump(log_entry_old, file, indent=4)
                
                print(f"Geloggte Durchschnittshumidity: {avg_temp}°C")
                print(f"Logdatei erstellt: {os.path.abspath(file_name)}")
                
            start_time = time.time()
            measurements = []

        time.sleep(interval_seconds)

if __name__ == "__main__":
    log_humidity()
