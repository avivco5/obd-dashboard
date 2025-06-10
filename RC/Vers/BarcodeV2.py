import csv
import os
import tkinter as tk
from tkinter import messagebox

FILE_PATH = "../inventory_remi.csv"



# יצירת קובץ ברירת מחדל אם לא קיים
def create_default_inventory():
    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'description', 'quantity'])

# טוען את הקובץ
def load_inventory():
    if not os.path.exists(FILE_PATH):
        create_default_inventory()

    inventory = {}
    with open(FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            barcode = row['barcode']
            inventory[barcode] = {
                'description': row['description'],
                'quantity': int(row['quantity'])
            }
    return inventory

# שומר את הקובץ
def save_inventory(inventory):
    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'description', 'quantity'])
        for barcode, item in inventory.items():
            writer.writerow([barcode, item['description'], item['quantity']])

# סריקת ברקוד
def on_barcode_enter(event=None):
    barcode = barcode_entry.get().strip()
    barcode_entry.delete(0, tk.END)

    if barcode in inventory:
        item = inventory[barcode]
        result.set(f"✅ {item['description']} - כמות: {item['quantity']}")
    else:
        result.set("❌ לא נמצא במלאי")

# הוספת פריט חדש
def add_new_item():
    barcode = new_barcode.get().strip()
    desc = new_desc.get().strip()
    qty = new_qty.get().strip()

    if not barcode or not desc or not qty.isdigit():
        messagebox.showerror("שגיאה", "נא למלא מק״ט, תיאור וכמות תקינה")
        return

    if barcode in inventory:
        messagebox.showerror("שגיאה", "פריט עם מק״ט זה כבר קיים")
        return

    inventory[barcode] = {"description": desc, "quantity": int(qty)}
    save_inventory(inventory)
    messagebox.showinfo("בוצע", f"הפריט '{desc}' נוסף בהצלחה!")

# הוספת כמות למלאי קיים
def add_to_existing_item():
    barcode = existing_barcode.get().strip()
    qty = existing_qty.get().strip()

    if barcode not in inventory:
        messagebox.showerror("שגיאה", "מק״ט לא נמצא במלאי")
        return
    if not qty.isdigit():
        messagebox.showerror("שגיאה", "כמות לא תקינה")
        return

    inventory[barcode]['quantity'] += int(qty)
    save_inventory(inventory)
    messagebox.showinfo("בוצע", f"הוספו {qty} יחידות ל־{inventory[barcode]['description']}")

# GUI ראשי
inventory = load_inventory()

root = tk.Tk()
root.title("ניהול מלאי - סורק ברקוד")

# סריקה
tk.Label(root, text="סרוק ברקוד:", font=('Arial', 14)).pack()
barcode_entry = tk.Entry(root, font=('Arial', 20))
barcode_entry.pack(padx=10, pady=10)
barcode_entry.bind("<Return>", on_barcode_enter)
barcode_entry.focus()

result = tk.StringVar()
tk.Label(root, textvariable=result, font=('Arial', 16)).pack(pady=10)

# הוספת פריט חדש
tk.Label(root, text="➕ הוספת פריט חדש:", font=('Arial', 14, 'bold')).pack(pady=5)

new_barcode = tk.Entry(root)
new_barcode.pack()
new_barcode.insert(0, "מקט חדש")

new_desc = tk.Entry(root)
new_desc.pack()
new_desc.insert(0, "תיאור פריט")

new_qty = tk.Entry(root)
new_qty.pack()
new_qty.insert(0, "כמות התחלתית")

tk.Button(root, text="הוסף פריט חדש", command=add_new_item).pack(pady=5)

# הוספה לפריט קיים
tk.Label(root, text="📦 הוספת כמות לפריט קיים:", font=('Arial', 14, 'bold')).pack(pady=5)

existing_barcode = tk.Entry(root)
existing_barcode.pack()
existing_barcode.insert(0, "מקט קיים")

existing_qty = tk.Entry(root)
existing_qty.pack()
existing_qty.insert(0, "כמות להוספה")

tk.Button(root, text="הוסף למלאי", command=add_to_existing_item).pack(pady=5)

root.mainloop()
