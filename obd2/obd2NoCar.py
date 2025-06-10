import random
import csv
import time
from datetime import datetime

filename = "obd_log.csv"
header = [
    "Time", "SPEED", "RPM", "THROTTLE", "ENGINE_LOAD", "INTAKE_PRESSURE",
    "INTAKE_TEMP", "COOLANT_TEMP", "FUEL_LEVEL", "RUN_TIME",
    "ACCELERATOR_POS_D", "CONTROL_MODULE_VOLTAGE", "RELATIVE_THROTTLE_POS",
    "BRAKE_PEDAL", "GEAR_ESTIMATE"
]

# ערכים התחלתיים
state = {
    "SPEED": 0,
    "RPM": 800,
    "THROTTLE": 10,
    "ENGINE_LOAD": 15,
    "FUEL_LEVEL": 80,
    "COOLANT_TEMP": 70,
    "RUN_TIME": 0
}

start_time = time.time()

def smooth_change(value, min_val, max_val, step=1):
    delta = random.uniform(-step, step)
    value = max(min_val, min(max_val, value + delta))
    return round(value, 2)

with open(filename, mode='w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()

    try:
        while True:
            now = datetime.now().strftime("%H:%M:%S")
            state["RUN_TIME"] = round(time.time() - start_time)

            state["SPEED"] = smooth_change(state["SPEED"], 0, 120, step=3)
            state["RPM"] = smooth_change(state["RPM"], 700, 5000, step=200)
            state["THROTTLE"] = smooth_change(state["THROTTLE"], 5, 90, step=4)
            state["ENGINE_LOAD"] = smooth_change(state["ENGINE_LOAD"], 10, 90)
            state["FUEL_LEVEL"] = smooth_change(state["FUEL_LEVEL"], 5, 100, step=0.1)
            state["COOLANT_TEMP"] = smooth_change(state["COOLANT_TEMP"], 70, 100, step=0.5)

            brake = 1 if state["THROTTLE"] < 10 and random.random() < 0.3 else 0
            gear = round(state["SPEED"] / state["RPM"] * 20) if state["RPM"] > 0 else 0

            row = {
                "Time": now,
                "SPEED": state["SPEED"],
                "RPM": state["RPM"],
                "THROTTLE": state["THROTTLE"],
                "ENGINE_LOAD": state["ENGINE_LOAD"],
                "INTAKE_PRESSURE": round(random.uniform(20, 100), 2),
                "INTAKE_TEMP": round(random.uniform(20, 60), 2),
                "COOLANT_TEMP": state["COOLANT_TEMP"],
                "FUEL_LEVEL": state["FUEL_LEVEL"],
                "RUN_TIME": state["RUN_TIME"],
                "ACCELERATOR_POS_D": round(state["THROTTLE"] + random.uniform(-3, 3), 2),
                "CONTROL_MODULE_VOLTAGE": round(random.uniform(13.0, 14.5), 2),
                "RELATIVE_THROTTLE_POS": round(state["THROTTLE"] / 1.5, 2),
                "BRAKE_PEDAL": brake,
                "GEAR_ESTIMATE": gear
            }

            writer.writerow(row)
            print(row)
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("📉 סימולציית OBD הופסקה")
