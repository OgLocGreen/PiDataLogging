import psutil
import time
import json
import random
import os
from datetime import datetime
import Adafruit_DHT


GPIO_PIN = 26

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

def read_dht_sensor(pin):
    sensor = Adafruit_DHT.DHT11
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return humidity, temperature


def log_dht(interval_seconds=1, log_interval=60):


    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(script_dir, "logging_data")
    os.makedirs(base_path, exist_ok=True)

    current_day = datetime.now().strftime('%Y-%m-%d')
    file_name_temperature = os.path.join(base_path, f"temperature_log_{current_day}.json")
    file_name_humidity = os.path.join(base_path, f"temperature_log_{current_day}.json")
    


    if os.path.exists(file_name_temperature):
        with open(file_name_temperature, "r") as file:
            try:
                log_temperature_old = json.load(file)
            except json.JSONDecodeError:
                log_temperature_old = []          
    else:
        log_temperature_old = []

    if os.path.exists(file_name_humidity):
        with open(file_name_humidity, "r") as file:
            try:
                log_humidity_old = json.load(file)
            except json.JSONDecodeError:
                log_humidity_old = []          
    else:
        log_humidity_old = []

    humidity_measurements = []
    temperature_measurements = [] 
    time.time()
    
    while True:
        now = datetime.now()
        new_day = now.strftime('%Y-%m-%d')
        if new_day != current_day:
            # Ein neuer Tag hat begonnen, aktualisiere den Dateinamen und leere die alte Eintragsliste
            current_day = new_day
            file_name_temperature = os.path.join(base_path, f"temperature_log_{current_day}.json")
            file_name_humidity = os.path.join(base_path, f"temperature_log_{current_day}.json")
            log_humidity_old = []
            log_humidity_old = []

        temp, humi = read_dht_sensor(GPIO_PIN)
        temperature_measurements.append(temp)
        humidity_measurements.append(humi)
        # Prüfe, ob es Zeit ist, den Mittelwert zu loggen
        if time.time() - start_time >= log_interval:
            if temperature_measurements:
                avg_temp = sum(temperature_measurements) / len(temperature_measurements)
                log_entry = {
                    "time": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "average_temperature": avg_temp
                }
                
                log_temperature_old.append(log_entry)
                # Schreibe die aktualisierten Daten in die Datei
                with open(file_name_temperature, "w") as file:
                    json.dump(log_temperature_old, file, indent=4)
                
                print(f"Geloggte Durchschnittstemperatur: {avg_temp}°C")
                print(f"Logdatei erstellt: {os.path.abspath(file_name_temperature)}")
            
            if humidity_measurements:
                avg_humi = sum(humidity_measurements) / len(humidity_measurements)
                log_entry = {
                    "time": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "average_humidity": avg_humi
                }
                log_humidity_old.append(log_entry)
                # Schreibe die aktualisierten Daten in die Datei
                with open(file_name_humidity, "w") as file:
                    json.dump(log_humidity_old, file, indent=4)
                
                print(f"Geloggte Durchschnittshumidity: {avg_humi}%")
                print(f"Logdatei erstellt: {os.path.abspath(file_name_humidity)}")

            start_time = time.time()
            humidity_measurements = []
            temperature_measurements = [] 

        time.sleep(interval_seconds)

if __name__ == "__main__":
    log_dht()
