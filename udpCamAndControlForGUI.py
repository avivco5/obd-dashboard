import cv2
import socket
import threading
import json
from flask import Flask, Response

# ------------------- UDP RECEIVER -------------------
UDP_IP = "0.0.0.0"
UDP_PORT = 9001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

def handle_udp():
    print(f"🟢 Listening for UDP on {UDP_IP}:{UDP_PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            msg = json.loads(data.decode())
            print(f"🎮 Received from {addr}: {msg}")
            # אפשר להוסיף כאן לוגיקה: שליטה פיזית, הדמיה וכו'
        except json.JSONDecodeError:
            print("❌ Bad JSON")

# ------------------- VIDEO STREAM -------------------
app = Flask(__name__)
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# ------------------- MAIN -------------------
if __name__ == "__main__":
    threading.Thread(target=handle_udp, daemon=True).start()
    threading.Thread(target=start_flask, daemon=True).start()

    print("✅ UDP + Video Flask server running...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n🛑 Shutting down.")
        sock.close()
        camera.release()
