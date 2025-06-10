
import csv
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
from PIL import Image, ImageTk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


FILE_PATH = "inventory_with_threshold.csv"
LOG_PATH = "log.csv"
ADMIN_PASSWORD = "5101"

current_user = None
inventory_started = False

cart = []  # הגדרה גלובלית בתחילת הקוד

def update_cart_display():
    cart_display.delete(0, tk.END)
    for item in cart:
        barcode = item['barcode']
        qty = item['qty']
        desc = inventory[barcode]["description"]
        cart_display.insert(tk.END, f"{desc} | מק\"ט: {barcode} | כמות: {qty}")

def pull_cart_items():
    if not current_user:
        messagebox.showerror("שגיאה", "משתמש לא מזוהה")
        return
    if not cart:
        messagebox.showinfo("ריק", "הסל ריק")
        return

    for barcode, qty in cart:
        if barcode not in inventory:
            messagebox.showerror("שגיאה", f"מקט {barcode} לא קיים במלאי")
            continue
        if inventory[barcode]['quantity'] < qty:
            messagebox.showerror("שגיאה", f"אין מספיק מלאי לפריט {barcode}")
            continue
        prev_qty = inventory[barcode]['quantity']
        inventory[barcode]['quantity'] -= qty
        log_action(current_user, "pull", barcode, inventory[barcode]['description'], qty)

    save_inventory(inventory)
    cart.clear()
    cart_display.delete(0, tk.END)
    #messagebox.showinfo("בוצע", "המשיכה מהסל הושלמה")
    def return_to_login():
        global current_user
        current_user = None
        user_frame.pack_forget()
        admin_frame.pack_forget()
        login_frame.pack(pady=50)
        user_entry.delete(0, tk.END)
        user_entry.focus_set()
        mode_label.config(text="מצב נוכחי: משיכת ציוד")

    messagebox.showinfo("בוצע", "✅ המשיכה מהסל הושלמה.\nמעבר למסך כניסה בעוד 10 שניות...")
    root.after(10000, return_to_login)



def add_to_cart():
    barcode = pull_barcode.get().strip()
    qty_str = pull_qty.get().strip()

    if not barcode or not qty_str.isdigit():
        messagebox.showerror("שגיאה", "יש להזין מק\"ט וכמות חוקית")
        return

    qty = int(qty_str)
    if barcode not in inventory:
        messagebox.showerror("שגיאה", "מק\"ט לא קיים במלאי")
        return

    available = inventory[barcode]["quantity"]

    for item in cart:
        if item['barcode'] == barcode:
            desc = inventory[barcode]["description"]
            current_qty = item['qty']

            def apply_choice(choice):
                nonlocal item
                if choice == "add":
                    new_qty = current_qty + qty
                else:  # "replace"
                    new_qty = qty

                if new_qty > available:
                    messagebox.showerror("שגיאה", f"אין מספיק מלאי. זמינות: {available}")
                    return

                item['qty'] = new_qty
                update_cart_display()
                dialog.destroy()

                # איפוס השדות והחזרת פוקוס למקט
                pull_barcode.delete(0, tk.END)
                pull_qty.delete(0, tk.END)
                pull_barcode.focus_set()

            # יצירת חלון בחירה
            dialog = tk.Toplevel(root)
            dialog.title("הפריט כבר קיים בסל")
            tk.Label(dialog, text=f"הפריט '{desc}' כבר קיים בסל עם כמות {current_qty}.").pack(pady=10)
            tk.Label(dialog, text=f"כמות חדשה משדה: {qty}").pack(pady=5)

            btn_frame = tk.Frame(dialog)
            btn_frame.pack(pady=10)

            tk.Button(btn_frame, text="➕ הוסף לכמות הקיימת", command=lambda: apply_choice("add")).grid(row=0, column=0, padx=5)
            tk.Button(btn_frame, text="✏️ שנה לכמות החדשה", command=lambda: apply_choice("replace")).grid(row=0, column=1, padx=5)

            return  # לא מוסיף כפול

    # אם לא קיים – הוסף רגיל
    if qty > available:
        pull_qty.delete(0, tk.END)
        pull_qty.insert(0, str(available))
        messagebox.showwarning("חוסר במלאי", f"אין מספיק מלאי. הכמות המרבית היא {available}.")
        return

    cart.append({'barcode': barcode, 'qty': qty})
    update_cart_display()
    pull_barcode.delete(0, tk.END)
    pull_qty.delete(0, tk.END)
    pull_barcode.focus_set()


def remove_selected_item():
    selected = cart_display.curselection()
    if not selected:
        messagebox.showwarning("שגיאה", "לא נבחר פריט להסרה")
        return
    index = selected[0]
    del cart[index]
    update_cart_display()

def edit_selected_item():
    selected = cart_display.curselection()
    if not selected:
        messagebox.showwarning("שגיאה", "לא נבחר פריט לעדכון")
        return
    index = selected[0]
    item = cart[index]

    # בקש כמות חדשה
    barcode = item['barcode']
    desc = inventory[barcode]["description"]
    new_qty_str = simpledialog.askstring("שנה כמות", f"הזן כמות חדשה עבור {desc}:", initialvalue=item['qty'])
    if not new_qty_str or not new_qty_str.isdigit():
        return

    new_qty = int(new_qty_str)
    barcode = item['barcode']
    current_qty_in_cart = sum(i['qty'] for i in cart if i['barcode'] == barcode) - item['qty']
    available_qty = inventory[barcode]['quantity']

    if new_qty + current_qty_in_cart > available_qty:
        messagebox.showerror("שגיאה", f"אין מספיק מלאי. זמינות: {available_qty - current_qty_in_cart}")
        return

    cart[index]['qty'] = new_qty
    update_cart_display()
def find_low_stock():
    low_items = []
    for barcode, item in inventory.items():
        threshold = item.get("threshold", 10)  # ברירת מחדל אם לא קיים
        if item["quantity"] < threshold:
            low_items.append((barcode, item["description"], item["quantity"], item.get("location", "לא ידוע")))
    return low_items


def show_low_stock():
    low_items = find_low_stock()
    if not low_items:
        messagebox.showinfo("חוסרים", "אין פריטים עם כמות נמוכה.")
        return

    win = tk.Toplevel(root)
    win.title("פריטים בחוסר")
    text = tk.Text(win, wrap="word", width=80, height=20)
    text.pack(padx=10, pady=10)

    for barcode, desc, qty, loc in low_items:
        text.insert("end", f"מקט: {barcode} | תיאור: {desc} | כמות: {qty} | מיקום: {loc}\n")

    def send_low_stock_email():
        try:
            send_email_low_stock(low_items)
        except Exception as e:
            messagebox.showerror("שגיאה בשליחה", str(e))

    tk.Button(win, text="שלח דוח במייל", command=send_low_stock_email).pack(pady=5)


def send_email_low_stock(items):
    from email.mime.text import MIMEText
    import smtplib

    sender = "avivcohenamp@gmail.com"
    password = "udss rufq tgnq dzka"
    receiver = "avivcohenamp@gmail.com"

    body = "דוח חוסרים:\n\n"
    for barcode, desc, qty, loc in items:
        body += f"מקט: {barcode} | תיאור: {desc} | כמות: {qty} | מיקום: {loc}\n"

    msg = MIMEText(body)
    msg["Subject"] = "📦 דוח חוסרים במלאי"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        messagebox.showinfo("הצלחה", "דוח החוסרים נשלח במייל בהצלחה!")
    except Exception as e:
        messagebox.showerror("שגיאה בשליחה", str(e))


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

def search_by_description():
    query = search_entry.get().strip().lower()
    if not query:
        messagebox.showerror("שגיאה", "נא להזין מחרוזת חיפוש")
        return

    results = []
    for barcode, item in inventory.items():
        if query in item['description'].lower():
            results.append(f"מקט: {barcode} | תיאור: {item['description']} | כמות: {item['quantity']}")

    if results:
        messagebox.showinfo("תוצאות חיפוש", "\n".join(results))
    else:
        messagebox.showinfo("תוצאות חיפוש", "לא נמצאו תוצאות התואמות לחיפוש.")

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
        return

    if len(matches) == 1:
        barcode, desc, qty, loc = matches[0]
        if not loc:
            loc = "לא ידוע"

        # מילוי אוטומטי של השדות
        pull_barcode.delete(0, tk.END)
        pull_barcode.insert(0, barcode)

        pull_qty.delete(0, tk.END)
        pull_qty.insert(0, "1")  # אפשר גם str(qty) אם אתה רוצה למלא את כל הכמות

        root.clipboard_clear()
        root.clipboard_append(barcode)

        messagebox.showinfo("הועתק ללוח",
                            f"הפריט היחיד נמצא והועתק ללוח:\nמקט: {barcode}\nתיאור: {desc}\nכמות: {qty}\nמיקום: {loc}")
        return

    # פתיחת חלון רק אם יש יותר מתוצאה אחת
    result_win = tk.Toplevel(root)
    result_win.title("תוצאות חיפוש")
    result_win.geometry("600x300")
    tk.Label(result_win, text="תוצאות:", font=("Arial", 12, "bold")).pack(pady=5)
    text_box = tk.Text(result_win, wrap="word", font=("Arial", 11))
    text_box.pack(expand=True, fill="both", padx=10, pady=10)

    for barcode, desc, qty, loc in matches:
        text_box.insert("end", f"מקט: {barcode} | תיאור: {desc} | כמות: {qty} | מיקום: {loc}\n")

    text_box.config(state="disabled")


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
                'location': row.get('location', 'לא ידוע'),
                'threshold': int(row.get('threshold', 10))  # ברירת מחדל אם אין עמודה כזו
            }
    return inventory

def save_inventory(inv):
    with open(FILE_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['barcode', 'description', 'quantity', 'location'])
        for barcode, item in inv.items():
            writer.writerow([barcode, item['description'], item['quantity'], item.get('location', '')])


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

def check_inventory_quantity():
    barcode = pull_barcode.get().strip()

    if not barcode:
        messagebox.showerror("שגיאה", "נא להזין מק\"ט")
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
    location = add_location.get().strip()
    threshold_str = add_threshold.get().strip()  # שדה חדש

    if not barcode or not desc or not qty_str or not location or not threshold_str:
        messagebox.showerror("שגיאה", "יש למלא את כל השדות: מק\"ט, תיאור, כמות, מיקום ורף אדום")
        return

    if not qty_str.isdigit() or not threshold_str.isdigit():
        messagebox.showerror("שגיאה", "כמות ורף אדום חייבים להיות מספרים שלמים")
        return

    if barcode in inventory:
        messagebox.showerror("שגיאה", "הפריט כבר קיים. השתמש בכפתור הוספת כמות")
        return

    inventory[barcode] = {
        'description': desc,
        'quantity': int(qty_str),
        'location': location,
        'threshold': int(threshold_str)
    }

    save_inventory(inventory)
    messagebox.showinfo("בוצע", f"הפריט {desc} נוסף למלאי עם כמות {qty_str} במיקום: {location} ורף אדום {threshold_str}")

    # איפוס השדות
    add_barcode.delete(0, tk.END)
    add_desc.delete(0, tk.END)
    add_qty.delete(0, tk.END)
    add_location.delete(0, tk.END)
    add_threshold.delete(0, tk.END)

def add_user():
    name = user_name_entry.get().strip()
    rfid = rfid_entry.get().strip()

    if not name or not rfid:
        messagebox.showerror("שגיאה", "יש להזין גם שם וגם מזהה RFID")
        return

    # יצירת הקובץ אם לא קיים
    if not os.path.exists("users.csv"):
        with open("users.csv", "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "rfid"])

    # בדיקת כפילויות
    with open("users.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["name"] == name:
                messagebox.showerror("שגיאה", f"השם '{name}' כבר קיים במערכת.")
                return
            if row["rfid"] == rfid:
                existing_name = row["name"]
                messagebox.showerror("שגיאה", f"מזהה ה-RFID '{rfid}' כבר משויך למשתמש : {existing_name}")
                return

    # הוספת המשתמש החדש
    with open("users.csv", "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, rfid])

    messagebox.showinfo("בוצע", f"המשתמש {name} נוסף בהצלחה!")
    user_name_entry.delete(0, tk.END)
    rfid_entry.delete(0, tk.END)

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
    update_log_display()

    # איפוס שדות
    existing_barcode.delete(0, tk.END)
    existing_qty.delete(0, tk.END)


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


def start_inventory_app():
    global inventory_started
    if inventory_started:
        return  # אל תוסיף שוב
    inventory_started = True

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
user_entry.focus_set()

def focus_next(event, widget_list, button=None):
    widget = event.widget
    if widget in widget_list:
        idx = widget_list.index(widget)
        if idx + 1 < len(widget_list):
            widget_list[idx + 1].focus_set()
        elif button:
            button.invoke()  # מפעיל את כפתור הפעולה

def handle_login():
    global current_user
    rfid = user_entry.get().strip()

    if not rfid:
        messagebox.showerror("שגיאה", "יש להזין מזהה RFID")
        return

    if not os.path.exists("users.csv"):
        messagebox.showerror("שגיאה", "לא קיימים משתמשים במערכת")
        return

    with open("users.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["rfid"] == rfid:
                current_user = row["name"]
                start_inventory_app()
                return


    def show_auto_closing_error(message):
        error_win = tk.Toplevel()
        error_win.title("שגיאה")
        error_win.geometry("300x100")
        error_win.attributes('-topmost', True)

        tk.Label(error_win, text=message, fg='red', font=('Arial', 12)).pack(expand=True)

        # סגירה אוטומטית אחרי 3 שניות
        error_win.after(3000, error_win.destroy)

    show_auto_closing_error("מזהה לא נמצא במערכת")
    user_entry.delete(0, tk.END)
    user_entry.focus_set()


tk.Button(login_frame, text="המשך", command=handle_login).pack(pady=5)

# כפתור נוסף לכניסת מנהל
def handle_admin_login():
    password = simpledialog.askstring("כניסת מנהל", "הזן סיסמת מנהל:", show="*")
    if password == ADMIN_PASSWORD:
        global current_user
        current_user = "admin"
        login_frame.pack_forget()
        admin_frame.pack(pady=10)
        update_log_display()
        root.geometry("1200x800")
        mode_label.config(text="מצב נוכחי: מנהל")
    else:
        messagebox.showerror("שגיאה", "סיסמה שגויה")

tk.Button(login_frame, text="כניסת מנהל 🔒", command=handle_admin_login).pack(pady=5)

login_frame.pack(pady=50)

# הפעלת התחברות גם על לחיצה על Enter
root.bind('<Return>', lambda event: handle_login())

mode_label = tk.Label(root, text="מצב נוכחי: משיכת ציוד", font=('Arial', 14, 'bold'))

user_frame = tk.Frame(root)
tk.Label(user_frame, text="📦 משיכת ציוד", font=('Arial', 14)).pack()
tk.Label(user_frame, text="מקט:").pack()
pull_barcode = tk.Entry(user_frame)
pull_barcode.pack()
tk.Label(user_frame, text="כמות למשיכה:").pack()
pull_qty = tk.Entry(user_frame)
pull_qty.pack()
arrow_frame_user = tk.Frame(user_frame)
arrow_frame_user.pack()
tk.Button(arrow_frame_user, text="+", command=lambda: increase_quantity(pull_qty)).grid(row=0, column=0)
tk.Button(arrow_frame_user, text="-", command=lambda: decrease_quantity(pull_qty)).grid(row=0, column=1)


# הוסף לסל
tk.Button(user_frame, text="➕ הוסף לסל", command=add_to_cart).pack(pady=3)



#שינוי פריט בסל
#tk.Button(user_frame, text="📝 שנה כמות לפריט נבחר", command=edit_selected_item).pack(pady=2)
#tk.Button(user_frame, text="❌ הסר פריט מהסל", command=remove_selected_item).pack(pady=2)

edit_remove_frame = tk.Frame(user_frame)
edit_remove_frame.pack(pady=5)

tk.Button(edit_remove_frame, text="📝 שנה כמות לפריט נבחר", command=edit_selected_item).grid(row=0, column=0, padx=5)
tk.Button(edit_remove_frame, text="❌ הסר פריט מהסל", command=remove_selected_item).grid(row=0, column=1, padx=5)

# הצגת הסל - חלון

cart_display = tk.Listbox(user_frame, width=60)
cart_display.pack()
# משוך את כל הסל
tk.Button(user_frame, text="✅ משוך פריטים מהסל", command=pull_cart_items).pack(pady=3)
tk.Label(user_frame, text="🔍 חיפוש לפי תיאור פריט:", font=('Arial', 12)).pack()
search_entry = tk.Entry(user_frame)
search_entry.pack()
search_entry.bind("<Return>", lambda event: search_barcode_by_description())

tk.Button(user_frame, text="חיפוש מק\"ט", command=search_barcode_by_description).pack(pady=5)


button_frame = tk.Frame(user_frame)
button_frame.pack(pady=5)

#pull_button = tk.Button(button_frame, text="משוך מהמלאי", command=pull_item)
#pull_button.grid(row=0, column=0, padx=5)

tk.Button(button_frame, text="📦 בדוק כמות", command=check_inventory_quantity).grid(row=0, column=1, padx=5)

tk.Button(button_frame, text="📉 הצג חוסרים", command=show_low_stock).grid(row=0, column=2, padx=5)

# התנהגות ENTER
pull_barcode.bind('<Return>', lambda e: pull_qty.focus_set())  # מעבר מהמק"ט לכמות
pull_qty.bind('<Return>', lambda e: add_to_cart())             # הוספה לסל
admin_frame = tk.Frame(root)

# הוספת כמות לפריט קיים

tk.Label(admin_frame, text="📥 הוספת כמות לפריט קיים", font=('Arial', 14)).pack(pady=5)
existing_item_frame = tk.Frame(admin_frame)
existing_item_frame.pack(pady=5)

tk.Label(existing_item_frame, text="מקט קיים").grid(row=0, column=1, padx=5, pady=2, sticky='w')
existing_barcode = tk.Entry(existing_item_frame)
existing_barcode.grid(row=0, column=0, padx=5, pady=2)

tk.Label(existing_item_frame, text="כמות להוספה").grid(row=1, column=1, padx=5, pady=2, sticky='w')
existing_qty = tk.Entry(existing_item_frame)
existing_qty.grid(row=1, column=0, padx=5, pady=2)

add_existing_button = tk.Button(existing_item_frame, text="הוסף למלאי", command=add_qty_to_existing)
add_existing_button.grid(row=2, column=0, columnspan=2, pady=5)

# קישורי אנטר בשדות לפריט קיים
existing_barcode.bind('<Return>', lambda e: existing_qty.focus_set())
existing_qty.bind('<Return>', lambda e: add_existing_button.invoke())

# הוספת פריט חדש

tk.Label(admin_frame, text="➕ הוספת פריט חדש", font=('Arial', 14)).pack()
new_item_frame = tk.Frame(admin_frame)
new_item_frame.pack(pady=5)

tk.Label(new_item_frame, text="מקט חדש").grid(row=0, column=1, padx=5, pady=2, sticky='w')
add_barcode = tk.Entry(new_item_frame)
add_barcode.grid(row=0, column=0, padx=5, pady=2)

tk.Label(new_item_frame, text="תיאור").grid(row=1, column=1, padx=5, pady=2, sticky='w')
add_desc = tk.Entry(new_item_frame)
add_desc.grid(row=1, column=0, padx=5, pady=2)

tk.Label(new_item_frame, text="כמות התחלתית").grid(row=2, column=1, padx=5, pady=2, sticky='w')
add_qty = tk.Entry(new_item_frame)
add_qty.grid(row=2, column=0, padx=5, pady=2)

tk.Label(new_item_frame, text="מיקום").grid(row=3, column=1, padx=5, pady=2, sticky='w')
add_location = tk.Entry(new_item_frame)
add_location.grid(row=3, column=0, padx=5, pady=2)

tk.Label(new_item_frame, text="רף אדום (סף חוסר לשליחת מייל)").grid(row=4, column=1, padx=5, pady=2, sticky='w')
add_threshold = tk.Entry(new_item_frame)
add_threshold.grid(row=4, column=0, padx=5, pady=2)

add_item_button = tk.Button(new_item_frame, text="הוסף פריט חדש", command=add_item)
add_item_button.grid(row=5, column=0, columnspan=2, pady=5)

# קישורי אנטר בשדות לפריט חדש
add_barcode.bind('<Return>', lambda e: add_desc.focus_set())
add_desc.bind('<Return>', lambda e: add_qty.focus_set())
add_qty.bind('<Return>', lambda e: add_location.focus_set())
add_location.bind('<Return>', lambda e: add_threshold.focus_set())
add_threshold.bind('<Return>', lambda e: add_item_button.invoke())

log_display = tk.StringVar()
tk.Label(admin_frame, textvariable=log_display, font=('Arial', 10), justify="left").pack(pady=10)

# 👤 ניהול משתמשים
tk.Label(admin_frame, text="👤 ניהול משתמשים", font=('Arial', 14)).pack(pady=10)
user_manage_frame = tk.Frame(admin_frame)
user_manage_frame.pack(pady=5)

tk.Label(user_manage_frame, text="שם משתמש:").grid(row=0, column=1, padx=5, pady=2, sticky='w')
user_name_entry = tk.Entry(user_manage_frame)
user_name_entry.grid(row=0, column=0, padx=5, pady=2)

tk.Label(user_manage_frame, text="מזהה RFID:").grid(row=1, column=1, padx=5, pady=2, sticky='w')
rfid_entry = tk.Entry(user_manage_frame)
rfid_entry.grid(row=1, column=0, padx=5, pady=2)

tk.Button(user_manage_frame, text="➕ הוסף משתמש", command=add_user).grid(row=2, column=0, columnspan=2, pady=5)

root.mainloop()
