from mfrc522 import SimpleMFRC522
import threading

reader = SimpleMFRC522()

def listen_for_rfid():
    while True:
        try:
            print("הנח תג...")
            id, text = reader.read()
            print(f"קיבלתי: {text}")
            user_entry.delete(0, 'end')
            user_entry.insert(0, text.strip())
        except Exception as e:
            print("שגיאה בקריאה:", e)
