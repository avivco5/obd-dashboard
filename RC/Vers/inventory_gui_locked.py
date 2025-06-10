
import csv
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

FILE_PATH = "inventory_gui_visible.csv"
ADMIN_PASSWORD = "5101"

def create_default_inventory():
    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'description', 'quantity'])
        writer.writerow(['7290108381917', 'remi', '3'])
        writer.writerow(['100001', 'Battery LiPo 3S 2200mAh', '15'])
        writer.writerow(['100002', 'Drone Flight Controller F4', '7'])
        writer.writerow(['100003', 'Brushless Motor 2306 2450KV', '20'])

def load_inventory():
    if not os.path.exists(FILE_PATH):
        create_default_inventory()
    inventory = {}
    with open(FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            inventory[row['barcode']] = {
                'description': row['description'],
                'quantity': int(row['quantity'])
            }
    return inventory

def save_inventory(inv):
    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'description', 'quantity'])
        for barcode, item in inv.items():
            writer.writerow([barcode, item['description'], item['quantity']])

inventory = load_inventory()

def switch_mode():
    if mode_label["text"] == "מצב נוכחי: משיכת ציוד":
        password = simpledialog.askstring("אימות", "נא להזין סיסמת מנהל:", show="*")
        if password == ADMIN_PASSWORD:
            mode_label.config(text="מצב נוכחי: מנהל")
            user_frame.pack_forget()
            admin_frame.pack(pady=10)
        else:
            messagebox.showerror("שגיאה", "סיסמה שגויה.")
    else:
        mode_label.config(text="מצב נוכחי: משיכת ציוד")
        admin_frame.pack_forget()
        user_frame.pack(pady=10)

def pull_item():
    barcode = pull_barcode.get().strip()
    qty_str = pull_qty.get().strip()

    if barcode not in inventory:
        messagebox.showerror("שגיאה", "מק״ט לא קיים במלאי")
        return
    if not qty_str.isdigit():
        messagebox.showerror("שגיאה", "כמות לא תקינה")
        return

    qty = int(qty_str)
    prev_qty = inventory[barcode]['quantity']
    if prev_qty < qty:
        messagebox.showerror("שגיאה", "אין מספיק מלאי")
        return

    inventory[barcode]['quantity'] -= qty
    new_qty = inventory[barcode]['quantity']
    save_inventory(inventory)

    messagebox.showinfo("בוצע", f"🔻 משיכה מהמלאי\n"
                                f"פריט: {inventory[barcode]['description']}\n"
                                f"מקט: {barcode}\n"
                                f"כמות קודמת: {prev_qty}\n"
                                f"נמשכה: {qty}\n"
                                f"כמות נוכחית: {new_qty}")

def add_item():
    barcode = add_barcode.get().strip()
    desc = add_desc.get().strip()
    qty_str = add_qty.get().strip()

    if not barcode or not desc or not qty_str.isdigit():
        messagebox.showerror("שגיאה", "נא להזין מק״ט, תיאור וכמות חוקית")
        return
    if barcode in inventory:
        messagebox.showerror("שגיאה", "הפריט כבר קיים. השתמש בכפתור הוספת כמות")
        return

    inventory[barcode] = {'description': desc, 'quantity': int(qty_str)}
    save_inventory(inventory)
    messagebox.showinfo("בוצע", f"הפריט {desc} נוסף למלאי עם כמות {qty_str}")

def add_qty_to_existing():
    barcode = existing_barcode.get().strip()
    qty_str = existing_qty.get().strip()

    if barcode not in inventory:
        messagebox.showerror("שגיאה", "מק״ט לא קיים במלאי")
        return
    if not qty_str.isdigit():
        messagebox.showerror("שגיאה", "כמות לא תקינה")
        return

    qty = int(qty_str)
    prev_qty = inventory[barcode]['quantity']
    inventory[barcode]['quantity'] += qty
    new_qty = inventory[barcode]['quantity']
    save_inventory(inventory)

    messagebox.showinfo("בוצע", f"✅ הוספת כמות למלאי\n"
                                f"פריט: {inventory[barcode]['description']}\n"
                                f"מקט: {barcode}\n"
                                f"כמות קודמת: {prev_qty}\n"
                                f"התווספו: {qty}\n"
                                f"כמות נוכחית: {new_qty}")

# GUI
root = tk.Tk()
root.title("ניהול מלאי - סורק ברקוד")

mode_label = tk.Label(root, text="מצב נוכחי: משיכת ציוד", font=('Arial', 14, 'bold'))
mode_label.pack(pady=5)

tk.Button(root, text="🔄 החלף מצב", command=switch_mode).pack(pady=5)

user_frame = tk.Frame(root)
tk.Label(user_frame, text="📦 משיכת ציוד", font=('Arial', 14)).pack()
tk.Label(user_frame, text="מקט:").pack()
pull_barcode = tk.Entry(user_frame)
pull_barcode.pack()
tk.Label(user_frame, text="כמות למשיכה:").pack()
pull_qty = tk.Entry(user_frame)
pull_qty.pack()
tk.Button(user_frame, text="משוך מהמלאי", command=pull_item).pack(pady=5)
user_frame.pack(pady=10)

admin_frame = tk.Frame(root)
tk.Label(admin_frame, text="➕ הוספת פריט חדש", font=('Arial', 14)).pack()
tk.Label(admin_frame, text="מקט חדש:").pack()
add_barcode = tk.Entry(admin_frame)
add_barcode.pack()
tk.Label(admin_frame, text="תיאור:").pack()
add_desc = tk.Entry(admin_frame)
add_desc.pack()
tk.Label(admin_frame, text="כמות התחלתית:").pack()
add_qty = tk.Entry(admin_frame)
add_qty.pack()
tk.Button(admin_frame, text="הוסף פריט חדש", command=add_item).pack(pady=5)

tk.Label(admin_frame, text="📥 הוספת כמות לפריט קיים", font=('Arial', 14)).pack(pady=5)
tk.Label(admin_frame, text="מקט קיים:").pack()
existing_barcode = tk.Entry(admin_frame)
existing_barcode.pack()
tk.Label(admin_frame, text="כמות להוספה:").pack()
existing_qty = tk.Entry(admin_frame)
existing_qty.pack()
tk.Button(admin_frame, text="הוסף למלאי", command=add_qty_to_existing).pack(pady=5)

root.mainloop()
