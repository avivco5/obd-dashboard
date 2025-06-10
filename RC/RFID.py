import csv
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
from PIL import Image, ImageTk

# RFID imports
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

FILE_PATH = "inventory_gui_visible.csv"
LOG_PATH = "../log.csv"
ADMIN_PASSWORD = "5101"

reader = SimpleMFRC522()

# כניסת זיהוי ראשונית עם תג RFID
def prompt_rfid_user():
    rfid_window = tk.Toplevel(root)
    rfid_window.title("זיהוי משתמש")
    rfid_window.geometry("400x200")
    tk.Label(rfid_window, text="נא הצמד תג לזיהוי", font=('Arial', 14)).pack(pady=40)

    def detect_tag():
        try:
            user, text = reader.read()
            user_id.insert(0, str(user))
            rfid_window.destroy()
        finally:
            GPIO.cleanup()

    root.after(1000, detect_tag)

# שאר הקוד נותר כפי שהיה - תוכל להוסיף את שאר הפונקציות כאן (load_inventory, save_inventory, log_action, pull_item וכו')
# לאחר מכן, תוכל להוסיף את קריאת prompt_rfid_user() בתחילת ה-mainloop כדי לזהות את המשתמש לפני הפעלת המערכת.

# GUI setup (השלם כפי שהיה)
root = tk.Tk()
root.title("ניהול מלאי - סורק ברקוד")
root.minsize(800, 600)
root.colormapwindows()

# שאר הגדרת GUI וכפתורים...

prompt_rfid_user()
root.mainloop()
