
import csv
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
from PIL import Image, ImageTk

FILE_PATH = "inventory_gui_visible.csv"
LOG_PATH = "log.csv"
ADMIN_PASSWORD = "5101"

current_user = None

def create_default_inventory():
    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'description', 'quantity'])
        writer.writerow(['7290108381917', 'remi', '3'])

def log_action(user, action, barcode, description, quantity):
    with open(LOG_PATH, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user,
            action,
            barcode,
            description,
            quantity
        ])

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
            update_log_display()
            root.geometry("1200x800")
        else:
            messagebox.showerror("שגיאה", "סיסמה שגויה.")
    else:
        mode_label.config(text="מצב נוכחי: משיכת ציוד")
        admin_frame.pack_forget()
        user_frame.pack(pady=10)
        root.geometry("600x500")

def update_log_display():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, newline='', encoding='utf-8') as f:
            lines = list(csv.reader(f))[1:]
            lines = lines[-10:][::-1]
            display_text = "פעולות אחרונות:\n"

            for row in lines:
                display_text += f"{row[0]} | {row[1]} | {row[2]} | {row[4]} | {row[5]}\n"

            log_display.set(display_text)
    else:
        log_display.set("אין פעולות רשומות עדיין.")

def pull_item():
    barcode = pull_barcode.get().strip()
    qty_str = pull_qty.get().strip()

    if not current_user:
        messagebox.showerror("שגיאה", "משתמש לא מזוהה")
        return
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
    log_action(current_user, "pull", barcode, inventory[barcode]['description'], qty)

    messagebox.showinfo("בוצע", f"🔻 משיכה מהמלאי\n"
                                f"משתמש: {current_user}\n"
                                f"פריט: {inventory[barcode]['description']}\n"
                                f"מקט: {barcode}\n"
                                f"כמות קודמת: {prev_qty}\n"
                                f"נמשכה: {qty}\n"
                                f"כמות נוכחית: {new_qty}")

def check_inventory_quantity():
    barcode = pull_barcode.get().strip()

    if not barcode:
        messagebox.showerror("שגיאה", "נא להזין מק"ט")
        return

    if barcode not in inventory:
        messagebox.showerror("לא נמצא", "הפריט לא קיים במלאי")
        return

    item = inventory[barcode]
    messagebox.showinfo("כמות במלאי", f"פריט: {item['description']}\nמקט: {barcode}\nכמות נוכחית: {item['quantity']}")

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
    log_action("admin", "add", barcode, inventory[barcode]['description'], qty)

    messagebox.showinfo("בוצע", f"✅ הוספת כמות למלאי\n"
                                f"פריט: {inventory[barcode]['description']}\n"
                                f"מקט: {barcode}\n"
                                f"כמות קודמת: {prev_qty}\n"
                                f"התווספו: {qty}\n"
                                f"כמות נוכחית: {new_qty}")
    update_log_display()

def start_inventory_app():
    login_frame.pack_forget()
    mode_label.pack(pady=5)
    tk.Button(root, text="🔄 החלף מצב", command=switch_mode).pack(pady=5)
    user_frame.pack(pady=10)

root = tk.Tk()
root.title("ניהול מלאי - מסך כניסה")
root.minsize(800, 600)

login_frame = tk.Frame(root)
tk.Label(login_frame, text="הזדהות משתמש", font=('Arial', 16)).pack(pady=10)
user_entry = tk.Entry(login_frame)
user_entry.pack(pady=5)

def handle_login():
    global current_user
    user = user_entry.get().strip()
    if user:
        current_user = user
        start_inventory_app()
    else:
        messagebox.showerror("שגיאה", "יש להזין מזהה משתמש")

tk.Button(login_frame, text="המשך", command=handle_login).pack(pady=5)
login_frame.pack(pady=50)

mode_label = tk.Label(root, text="מצב נוכחי: משיכת ציוד", font=('Arial', 14, 'bold'))

user_frame = tk.Frame(root)
tk.Label(user_frame, text="📦 משיכת ציוד", font=('Arial', 14)).pack()
tk.Label(user_frame, text="מקט:").pack()
pull_barcode = tk.Entry(user_frame)
pull_barcode.pack()
tk.Label(user_frame, text="כמות למשיכה:").pack()
pull_qty = tk.Entry(user_frame)
pull_qty.pack()

button_frame = tk.Frame(user_frame)
button_frame.pack(pady=5)
tk.Button(button_frame, text="משוך מהמלאי", command=pull_item).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="📦 בדוק כמות", command=check_inventory_quantity).grid(row=0, column=1, padx=5)

admin_frame = tk.Frame(root)
tk.Label(admin_frame, text="➕ הוספת פריט חדש", font=('Arial', 14)).pack()
add_barcode = tk.Entry(admin_frame)
add_desc = tk.Entry(admin_frame)
add_qty = tk.Entry(admin_frame)
tk.Label(admin_frame, text="מקט חדש:").pack()
add_barcode.pack()
tk.Label(admin_frame, text="תיאור:").pack()
add_desc.pack()
tk.Label(admin_frame, text="כמות התחלתית:").pack()
add_qty.pack()
tk.Button(admin_frame, text="הוסף פריט חדש", command=add_item).pack(pady=5)

tk.Label(admin_frame, text="📥 הוספת כמות לפריט קיים", font=('Arial', 14)).pack(pady=5)
existing_barcode = tk.Entry(admin_frame)
existing_qty = tk.Entry(admin_frame)
tk.Label(admin_frame, text="מקט קיים:").pack()
existing_barcode.pack()
tk.Label(admin_frame, text="כמות להוספה:").pack()
existing_qty.pack()
tk.Button(admin_frame, text="הוסף למלאי", command=add_qty_to_existing).pack(pady=5)

log_display = tk.StringVar()
tk.Label(admin_frame, textvariable=log_display, font=('Arial', 10), justify="left").pack(pady=10)

root.mainloop()
