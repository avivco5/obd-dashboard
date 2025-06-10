import obd
import time
import csv
import os
from datetime import datetime

# התחברות
connection = obd.OBD(portstr="/dev/rfcomm0")
if not connection.is_connected():
    print("❌ חיבור נכשל")
    exit()
print("✅ מחובר ל-OBD\n")

# רשימת פקודות
commands = {
    "SPEED": obd.commands.SPEED,
    "RPM": obd.commands.RPM,
    "THROTTLE": obd.commands.THROTTLE_POS,
    "ENGINE_LOAD": obd.commands.ENGINE_LOAD,
    "INTAKE_PRESSURE": obd.commands.INTAKE_PRESSURE,
    "INTAKE_TEMP": obd.commands.INTAKE_TEMP,
    "COOLANT_TEMP": obd.commands.COOLANT_TEMP,
    "FUEL_LEVEL": obd.commands.FUEL_LEVEL,
    "RUN_TIME": obd.commands.RUN_TIME,
    "ACCELERATOR_POS_D": obd.commands.ACCELERATOR_POS_D,
    "CONTROL_MODULE_VOLTAGE": obd.commands.CONTROL_MODULE_VOLTAGE,
    "RELATIVE_THROTTLE_POS": obd.commands.RELATIVE_THROTTLE_POS,
}

# ניסיון להוסיף דוושת בלמים
try:
    commands["BRAKE_PEDAL"] = obd.commands.BRAKE_PEDAL
except AttributeError:
    pass  # לא נתמך בספרייה

# פונקציית חישוב הילוך
def estimate_gear(speed, rpm):
    if speed is None or rpm is None or rpm.magnitude == 0:
        return None
    ratio = speed.magnitude / rpm.magnitude
    return round(ratio * 20)

# הכנת קובץ CSV
filename = "obd_log.csv"
header = ["Time"] + list(commands.keys()) + ["GEAR_ESTIMATE"]
file_exists = os.path.isfile(filename)

with open(filename, mode='a', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)

    if not file_exists:
        writer.writeheader()

    try:
        while True:
            row = {"Time": datetime.now().strftime("%H:%M:%S")}
            values = {}

            for name, cmd in commands.items():
                if connection.supports(cmd):
                    response = connection.query(cmd)
                    values[name] = response.value
                    print(f"{name}: {response.value}")
                    row[name] = response.value.magnitude if response.value else None
                else:
                    row[name] = None

            gear = estimate_gear(values.get("SPEED"), values.get("RPM"))
            row["GEAR_ESTIMATE"] = gear
            print(f"GEAR_ESTIMATE: {gear}")
            writer.writerow(row)
            print("-" * 50)
            time.sleep(1)

    except KeyboardInterrupt:
        print("עצירה על ידי המשתמש")
        connection.close()
import obd
import time
import csv
import os
from datetime import datetime

# התחברות
connection = obd.OBD(portstr="/dev/rfcomm0")
if not connection.is_connected():
    print("❌ חיבור נכשל")
    exit()
print("✅ מחובר ל-OBD\n")

# רשימת פקודות
commands = {
    "SPEED": obd.commands.SPEED,
    "RPM": obd.commands.RPM,
    "THROTTLE": obd.commands.THROTTLE_POS,
    "ENGINE_LOAD": obd.commands.ENGINE_LOAD,
    "INTAKE_PRESSURE": obd.commands.INTAKE_PRESSURE,
    "INTAKE_TEMP": obd.commands.INTAKE_TEMP,
    "COOLANT_TEMP": obd.commands.COOLANT_TEMP,
    "FUEL_LEVEL": obd.commands.FUEL_LEVEL,
    "RUN_TIME": obd.commands.RUN_TIME,
    "ACCELERATOR_POS_D": obd.commands.ACCELERATOR_POS_D,
    "CONTROL_MODULE_VOLTAGE": obd.commands.CONTROL_MODULE_VOLTAGE,
    "RELATIVE_THROTTLE_POS": obd.commands.RELATIVE_THROTTLE_POS,
}

# ניסיון להוסיף דוושת בלמים
try:
    commands["BRAKE_PEDAL"] = obd.commands.BRAKE_PEDAL
except AttributeError:
    pass  # לא נתמך בספרייה

# פונקציית חישוב הילוך
def estimate_gear(speed, rpm):
    if speed is None or rpm is None or rpm.magnitude == 0:
        return None
    ratio = speed.magnitude / rpm.magnitude
    return round(ratio * 20)

# הכנת קובץ CSV
filename = "obd_log.csv"
header = ["Time"] + list(commands.keys()) + ["GEAR_ESTIMATE"]
file_exists = os.path.isfile(filename)

with open(filename, mode='a', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)

    if not file_exists:
        writer.writeheader()

    try:
        while True:
            row = {"Time": datetime.now().strftime("%H:%M:%S")}
            values = {}

            for name, cmd in commands.items():
                if connection.supports(cmd):
                    response = connection.query(cmd)
                    values[name] = response.value
                    print(f"{name}: {response.value}")
                    row[name] = response.value.magnitude if response.value else None
                else:
                    row[name] = None

            gear = estimate_gear(values.get("SPEED"), values.get("RPM"))
            row["GEAR_ESTIMATE"] = gear
            print(f"GEAR_ESTIMATE: {gear}")
            writer.writerow(row)
            print("-" * 50)
            time.sleep(1)

    except KeyboardInterrupt:
        print("עצירה על ידי המשתמש")
        connection.close()
