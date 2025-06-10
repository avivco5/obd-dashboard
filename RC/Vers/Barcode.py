import csv
import tkinter as tk
from tkinter import messagebox

# טוען את רשימת המלאי מקובץ CSV
def load_inventory(file_path="inventory_remi.csv"):
    inventory = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            barcode = row['barcode']
            inventory[barcode] = {
                'description': row['description'],
                'quantity': int(row['quantity'])
            }
    return inventory

# פעולה כשלוחצים Enter אחרי סריקת ברקוד
def on_barcode_enter(event):
    barcode = entry.get().strip()
    entry.delete(0, tk.END)

    if barcode in inventory:
        item = inventory[barcode]
        result.set(f"✅ {item['description']} - כמות במלאי: {item['quantity']}")
    else:
        result.set("❌ פריט לא נמצא במלאי")

# יצירת GUI
inventory = load_inventory()

root = tk.Tk()
root.title("מערכת ניהול מלאי - סורק ברקוד")

entry = tk.Entry(root, font=('Arial', 24))
entry.pack(padx=20, pady=20)
entry.bind("<Return>", on_barcode_enter)
entry.focus()

result = tk.StringVar()
result_label = tk.Label(root, textvariable=result, font=('Arial', 20))
result_label.pack(padx=20, pady=20)

root.mainloop()
