import tkinter as tk
from tkinter import messagebox
import csv
import os

FILE_PATH = "inventory_gui.csv"

def create_default_inventory():
    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'description', 'quantity'])

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

def save_inventory(inventory):
    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'description', 'quantity'])
        for barcode, item in inventory.items():
            writer.writerow([barcode, item['description'], item['quantity']])

inventory = load_inventory()

def switch_mode():
    if mode_label["text"] == "מצב נוכחי: משיכת ציוד":
        mode_label.config(text="מצב נוכחי: מנהל")
        user_frame.pack_forget()
        admin_frame.pack(pady=10)
    else:
        mode_label.config(text="מצב נוכחי: משיכת ציוד")
        admin_frame.pack_forget()
        user_frame.pack(pady=10)

def pull_item():
    barcode = pull_barcode.get().strip()
    qty = pull_qty.get().strip()

    if barcode not in inventory:
        messagebox.showerror("שגיאה", "מק״ט לא קיים במלאי")
        return
    if not qty.isdigit():
        messagebox.showerror("שגיאה", "כמות לא תקינה")
        return
    qty = int(qty)
    if inventory[barcode]['quantity'] < qty:
        messagebox.showerror("שגיאה", "אין מספיק מלאי")
        return

    inventory[barcode]['quantity'] -= qty
    save_inventory(inventory)
    messagebox.showinfo("בוצע", f"הוצאה של {qty} יחידות מהפריט: {inventory[barcode]['description']}")

def add_item():
    barcode = add_barcode.get().strip()
    desc = add_desc.get().strip()
    qty = add_qty.get().strip()

    if not barcode or not desc or not qty.isdigit():
        messagebox.showerror("שגיאה", "נא להזין מק״ט, תיאור וכמות חוקית")
        return

    if barcode in inventory:
        messagebox.showerror("שגיאה", "הפריט כבר קיים. השתמש בכפתור הוספת כמות")
        return

    inventory[barcode] = {'description': desc, 'quantity': int(qty)}
    save_inventory(inventory)
    messagebox.showinfo("בוצע", f"הפריט {desc} נוסף למלאי")

def add_qty_to_existing():
    barcode = existing_barcode.get().strip()
    qty = existing_qty.get().strip()

    if barcode not in inventory:
        messagebox.showerror("שגיאה", "מק״ט לא קיים במלאי")
        return
    if not qty.isdigit():
        messagebox.showerror("שגיאה", "כמות לא תקינה")
        return

    inventory[barcode]['quantity'] += int(qty)
    save_inventory(inventory)
    messagebox.showinfo("בוצע", f"הוספו {qty} יחידות לפריט: {inventory[barcode]['description']}")

root = tk.Tk()
root.title("ניהול מלאי - סורק ברקוד")

mode_label = tk.Label(root, text="מצב נוכחי: משיכת ציוד", font=('Arial', 14, 'bold'))
mode_label.pack(pady=5)

tk.Button(root, text="🔄 החלף מצב", command=switch_mode).pack(pady=5)

user_frame = tk.Frame(root)

tk.Label(user_frame, text="📦 משיכת ציוד", font=('Arial', 14)).pack()
pull_barcode = tk.Entry(user_frame)
pull_barcode.pack()
pull_barcode.insert(0, "מקט")
pull_qty = tk.Entry(user_frame)
pull_qty.pack()
pull_qty.insert(0, "כמות למשיכה")
tk.Button(user_frame, text="משוך מהמלאי", command=pull_item).pack(pady=5)

user_frame.pack(pady=10)

admin_frame = tk.Frame(root)

tk.Label(admin_frame, text="➕ הוספת פריט חדש", font=('Arial', 14)).pack()
add_barcode = tk.Entry(admin_frame)
add_barcode.pack()
add_barcode.insert(0, "מקט חדש")
add_desc = tk.Entry(admin_frame)
add_desc.pack()
add_desc.insert(0, "תיאור")
add_qty = tk.Entry(admin_frame)
add_qty.pack()
add_qty.insert(0, "כמות התחלתית")
tk.Button(admin_frame, text="הוסף פריט חדש", command=add_item).pack(pady=5)

tk.Label(admin_frame, text="📥 הוספת כמות לפריט קיים", font=('Arial', 14)).pack(pady=5)
existing_barcode = tk.Entry(admin_frame)
existing_barcode.pack()
existing_barcode.insert(0, "מקט קיים")
existing_qty = tk.Entry(admin_frame)
existing_qty.pack()
existing_qty.insert(0, "כמות להוספה")
tk.Button(admin_frame, text="הוסף למלאי", command=add_qty_to_existing).pack(pady=5)

root.mainloop()
