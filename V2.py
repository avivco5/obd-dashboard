import cv2
import socket
import threading
import json
from flask import Flask, Response, request, jsonify

# ------------------- UDP RECEIVER -------------------
UDP_IP = "0.0.0.0"
UDP_PORT = 9001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

current_gear = 1500  # N (ברירת מחדל)

def handle_udp():
    global current_gear
    print(f"🟢 Listening for UDP on {UDP_IP}:{UDP_PORT}")
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            msg = json.loads(data.decode())
            if "gear" in msg:
                current_gear = msg["gear"]
            print(f"🎮 Received from {addr}: {msg}")
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

# ------------------- GEAR CONTROL ENDPOINT -------------------
@app.route('/set_gear', methods=['POST'])
def set_gear():
    global current_gear
    try:
        data = request.json
        gear = int(data.get("gear", 1500))
        if gear in [1000, 1500, 2000]:
            current_gear = gear
            print(f"⚙️ Gear manually set to: {current_gear}")
            return jsonify({"status": "ok", "gear": current_gear})
        else:
            return jsonify({"status": "error", "msg": "Invalid gear value"}), 400
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/gear', methods=['GET'])
def get_gear():
    return jsonify({"gear": current_gear})

def start_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# ------------------- MAIN -------------------
if __name__ == "__main__":
    threading.Thread(target=handle_udp, daemon=True).start()
    threading.Thread(target=start_flask, daemon=True).start()

    print("✅ UDP + Video + Gea"
          "r Flask server running...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n🛑 Shutting down.")
        sock.close()
        camera.release()

