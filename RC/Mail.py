import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, message_body):
    sender_email = "avivcohenamp@gmail.com"
    sender_password = "uAAAAAAAAAA"  # לא הסיסמה הרגילה – ראה הסבר למטה
    receiver_email = "avivcohenamp@gmail.com"  # כאן אתה שם את מי שאתה רוצה לשלוח אליו

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message_body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("המייל נשלח בהצלחה!")
    except Exception as e:
        print("שגיאה בשליחת מייל:", e)

# דוגמה לשימוש:
send_email("target@gmail.com", "בדיקה", "שלום, זה מייל אוטומטי ממערכת המלאי.")
