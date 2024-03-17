import json
import os
import time
from datetime import datetime
import logging
import random

# Konfigurieren des Logging-Moduls
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_sensor_data(sensor_type):
    try:
        if sensor_type == "temp":
            return get_cpu_temperature()
        elif sensor_type == "hum_air":
            return get_humidity_air()
        elif sensor_type == "hum_soil":
            return get_humidity_soil()
    except Exception as e:
        logging.error(f"Fehler beim Auslesen des Sensors {sensor_type}: {e}")
        return random.randint(90, 99)  # Simulierter Sensorwert bei Fehler

def log_measurements(name, measurements, base_path, current_day):
    file_name = os.path.join(base_path, f"{name}_{current_day}.json")
    with open(file_name, "w") as file:
        json.dump(measurements, file, indent=4)
    logging.info(f"Logdatei aktualisiert: {os.path.abspath(file_name)}")

def create_log_entry(measurements, sensor_type):
    avg_value = sum(measurements) / len(measurements)
    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        f"average_{sensor_type}": avg_value
    }
    logging.info(f"Geloggter Durchschnittswert: {avg_value}")
    return log_entry

def logger(sensor_type="temp", name="sensor_log", interval_seconds=1, log_interval=60):
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging_data")
    os.makedirs(base_path, exist_ok=True)
    
    current_day = datetime.now().strftime('%Y-%m-%d')
    measurements = []
    log_entry_old = []
    start_time = time.time()

    while True:
        if datetime.now().strftime('%Y-%m-%d') != current_day:
            # Neuer Tag, leere die alte Eintragsliste und aktualisiere den Tag
            current_day = datetime.now().strftime('%Y-%m-%d')
            log_entry_old = []

        sensor_value = get_sensor_data(sensor_type)
        logging.info(f"Aktueller Sensorwert: {sensor_value}")
        measurements.append(sensor_value)

        if time.time() - start_time >= log_interval:
            if measurements:
                log_entry = create_log_entry(measurements, sensor_type)
                log_entry_old.append(log_entry)
                log_measurements(name, log_entry_old, base_path, current_day)
                measurements = []  # Reset measurements for the next interval
                start_time = time.time()

        time.sleep(interval_seconds)

if __name__ == "__main__":
    logger()