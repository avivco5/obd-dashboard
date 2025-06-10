import csv
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

FILE_PATH = "inventory_gui_visible.csv"
LOG_PATH = "log.csv"
ADMIN_PASSWORD = "5101"

current_user = None
inventory_started = False

def create_default_inventory():
    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'description', 'quantity', 'location'])
        writer.writerow(['7290108381917', 'remi', '3', 'ארון 1'])

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
                'quantity': int(row['quantity']),
                'location': row.get('location', 'לא ידוע')
            }
    return inventory

def save_inventory(inv):
    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'description', 'quantity', 'location'])
        for barcode, item in inv.items():
            writer.writerow([barcode, item['description'], item['quantity'], item.get('location', '')])

def focus_next(event, widget_list, button=None):
    widget = event.widget
    if widget in widget_list:
        idx = widget_list.index(widget)
        if idx + 1 < len(widget_list):
            widget_list[idx + 1].focus_set()
        elif button:
            button.invoke()

def increase_quantity(entry):
    val = entry.get()
    try:
        num = int(val)
    except:
        num = 0
    entry.delete(0, tk.END)
    entry.insert(0, str(num + 1))

def decrease_quantity(entry):
    val = entry.get()
    try:
        num = int(val)
    except:
        num = 0
    entry.delete(0, tk.END)
    entry.insert(0, str(max(num - 1, 0)))

def search_barcode_by_description():
    term = search_entry.get().strip().lower()
    if not term:
        messagebox.showwarning("שגיאה", "נא להזין טקסט לחיפוש")
        return

    matches = []
    for barcode, item in inventory.items():
        desc = item["description"].lower()
        location = item.get("location", "").lower()
        if term in barcode.lower() or term in desc or term in location:
            matches.append((barcode, item["description"], item["quantity"], item.get("location", "לא ידוע")))

    if not matches:
        messagebox.showinfo("אין תוצאות", "לא נמצאו פריטים תואמים")
    elif len(matches) == 1:
        barcode = matches[0][0]
        root.clipboard_clear()
        root.clipboard_append(barcode)
        messagebox.showinfo("הועתק ללוח", f"מקט {barcode} הועתק ללוח")
    else:
        result_win = tk.Toplevel(root)
        result_win.title("תוצאות חיפוש")
        result_win.geometry("600x300")
        tk.Label(result_win, text="תוצאות:", font=("Arial", 12, "bold")).pack(pady=5)
        text_box = tk.Text(result_win, wrap="word", font=("Arial", 11))
        text_box.pack(expand=True, fill="both", padx=10, pady=10)

        for barcode, desc, qty, loc in matches:
            text_box.insert("end", f"מקט: {barcode} | תיאור: {desc} | כמות: {qty} | מיקום: {loc}\n")

        text_box.config(state="disabled")

def pull_item():
    barcode = pull_barcode.get().strip()
    qty_str = pull_qty.get().strip()

    if not current_user:
        messagebox.showerror("שגיאה", "משתמש לא מזוהה")
        return
    if barcode not in inventory:
        messagebox.showerror("שגיאה", "מק\"ט לא קיים במלאי")
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

    messagebox.showinfo("בוצע", f"🔻 משיכה מהמלאי\nמשתמש: {current_user}\nפריט: {inventory[barcode]['description']}\nמקט: {barcode}\nכמות קודמת: {prev_qty}\nנמשכה: {qty}\nכמות נוכחית: {new_qty}")

def add_item():
    barcode = add_barcode.get().strip()
    desc = add_desc.get().strip()
    qty_str = add_qty.get().strip()
    location = add_location.get().strip()

    if not barcode or not desc or not qty_str.isdigit():
        messagebox.showerror("שגיאה", "נא להזין מק\"ט, תיאור וכמות חוקית")
        return
    if barcode in inventory:
        messagebox.showerror("שגיאה", "הפריט כבר קיים. השתמש בכפתור הוספת כמות")
        return

    inventory[barcode] = {
        'description': desc,
        'quantity': int(qty_str),
        'location': location
    }

    save_inventory(inventory)
    messagebox.showinfo("בוצע", f"הפריט {desc} נוסף למלאי עם כמות {qty_str} במיקום: {location}")

def add_qty_to_existing():
    barcode = existing_barcode.get().strip()
    qty_str = existing_qty.get().strip()

    if barcode not in inventory:
        messagebox.showerror("שגיאה", "מק\"ט לא קיים במלאי")
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

    messagebox.showinfo("בוצע", f"✅ הוספת כמות למלאי\nפריט: {inventory[barcode]['description']}\nמקט: {barcode}\nכמות קודמת: {prev_qty}\nהתווספו: {qty}\nכמות נוכחית: {new_qty}")

def start_inventory_app():
    global inventory_started
    if inventory_started:
        return
    inventory_started = True

    login_frame.pack_forget()
    mode_label.pack(pady=5)
    tk.Button(root, text="🔄 החלף מצב", command=switch_mode).pack(pady=5)
    user_frame.pack(pady=10)

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

def handle_login():
    global current_user
    user = user_entry.get().strip()
    if user:
        current_user = user
        start_inventory_app()
    else:
        messagebox.showerror("שגיאה", "יש להזין מזהה משתמש")

inventory = load_inventory()

root = tk.Tk()
root.title("ניהול מלאי")
root.minsize(800, 600)

login_frame = tk.Frame(root)
tk.Label(login_frame, text="הזדהות משתמש", font=('Arial', 16)).pack(pady=10)
user_entry = tk.Entry(login_frame)
user_entry.pack(pady=5)
tk.Button(login_frame, text="המשך", command=handle_login).pack(pady=5)
login_frame.pack(pady=50)

root.bind('<Return>', lambda event: handle_login())

mode_label = tk.Label(root, text="מצב נוכחי: משיכת ציוד", font=('Arial', 14, 'bold'))

# User Frame
user_frame = tk.Frame(root)
tk.Label(user_frame, text="📦 משיכת ציוד", font=('Arial', 14)).pack()
tk.Label(user_frame, text="מקט:").pack()
pull_barcode = tk.Entry(user_frame)
pull_barcode.pack()
tk.Label(user_frame, text="כמות למשיכה:").pack()
pull_qty = tk.Entry(user_frame)
pull_qty.pack()
arrow_frame_user = tk.Frame(user_frame)
narrow_frame_user.pack()
tk.Button(narrow_frame_user, text="+", command=lambda: increase_quantity(pull_qty)).grid(row=0, column=0)
tk.Button(narrow_frame_user, text="-", command=lambda: decrease_quantity(pull_qty)).grid(row=0, column=1)

tk.Label(user_frame, text="🔍 חיפוש לפי תיאור/מקט/מיקום:", font=('Arial', 12)).pack()
search_entry = tk.Entry(user_frame)
search_entry.pack()
search_entry.bind("<Return>", lambda event: search_barcode_by_description())
tk.Button(user_frame, text="🔎 חפש מק\"ט", command=search_barcode_by_description).pack(pady=5)

pull_button = tk.Button(user_frame, text="משוך מהמלאי", command=pull_item)
pull_button.pack(pady=5)

pull_fields = [pull_barcode, pull_qty]
for field in pull_fields:
    field.bind('<Return>', lambda e, fields=pull_fields, btn=pull_button: focus_next(e, fields, btn))

# Admin Frame
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
tk.Label(admin_frame, text="מיקום:").pack()
add_location = tk.Entry(admin_frame)
add_location.pack()
arrow_frame_admin = tk.Frame(admin_frame)
narrow_frame_admin.pack()
tk.Button(narrow_frame_admin, text="+", command=lambda: increase_quantity(add_qty)).grid(row=0, column=0)
tk.Button(narrow_frame_admin, text="-", command=lambda: decrease_quantity(add_qty)).grid(row=0, column=1)

add_button = tk.Button(admin_frame, text="הוסף פריט חדש", command=add_item)
add_button.pack(pady=5)

add_fields = [add_barcode, add_desc, add_qty, add_location]
for field in add_fields:
    field.bind('<Return>', lambda e, fields=add_fields, btn=add_button: focus_next(e, fields, btn))

# הוספת כמות לפריט קיים
existing_barcode = tk.Entry(admin_frame)
existing_qty = tk.Entry(admin_frame)
tk.Label(admin_frame, text="\n📥 הוספת כמות לפריט קיים", font=('Arial', 14)).pack(pady=5)
tk.Label(admin_frame, text="מקט קיים:").pack()
existing_barcode.pack()
tk.Label(admin_frame, text="כמות להוספה:").pack()
existing_qty.pack()
arrow_frame_exist = tk.Frame(admin_frame)
narrow_frame_exist.pack()
tk.Button(narrow_frame_exist, text="+", command=lambda: increase_quantity(existing_qty)).grid(row=0, column=0)
tk.Button(narrow_frame_exist, text="-", command=lambda: decrease_quantity(existing_qty)).grid(row=0, column=1)

add_qty_button = tk.Button(admin_frame, text="הוסף למלאי", command=add_qty_to_existing)
add_qty_button.pack(pady=5)

exist_fields = [existing_barcode, existing_qty]
for field in exist_fields:
    field.bind("<Return>", lambda e, fields=exist_fields, btn=add_qty_button: focus_next(e, fields, btn))

log_display = tk.StringVar()
tk.Label(admin_frame, textvariable=log_display, font=('Arial', 10), justify="left").pack(pady=10)

root.mainloop()
