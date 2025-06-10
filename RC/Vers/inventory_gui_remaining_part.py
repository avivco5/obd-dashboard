
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
