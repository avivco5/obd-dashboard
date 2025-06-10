import pandas as pd
import matplotlib.pyplot as plt

# טען את הקובץ
df = pd.read_csv("obd_log.csv")

# הפוך את עמודת הזמן לאינדקס
df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S")
df.set_index("Time", inplace=True)

# בחר אילו עמודות להציג
columns_to_plot = [
    "SPEED",
    "RPM",
    "THROTTLE",
    "BRAKE_PEDAL",         # רק אם קיים
    "GEAR_ESTIMATE"
]

# סינון לעמודות שקיימות בפועל
available_columns = [col for col in columns_to_plot if col in df.columns]

# ציור הגרף
df[available_columns].plot(figsize=(12, 6), marker='o')
plt.title("OBD2 Live Data")
plt.xlabel("Time")
plt.ylabel("Values")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
