import socket
import struct
from evdev import InputDevice, ecodes

# Raspberry Pi IP and UDP port (change if testing locally or remote)
PI_IP = '127.0.0.1'
PI_PORT = 9001

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

device = InputDevice('/dev/input/event6')  # Change to your device path

# Initialize all channels to idle/neutral values
gear_rc_value = 1000  # Start gear down
steering_rc_value = 1500
brake_rc_value = 1000
gas_rc_value = 1000
arm_safety_rc_value = 1000
arm_rc_value = 1000
cart_rc_value = 1000
camera_rc_value = 1000

def normalize_axis(value, invert=False):
    # Normalize axis from -32768..32767 to 1000..2000
    norm = (value + 32768) / 65535  # 0..1
    if invert:
        norm = 1 - norm
    return int(1000 + norm * 1000)

# Map evdev axis code to variable names
AXIS_MAP = {
    3: 'steering_rc_value',
    1: 'brake_rc_value',
    4: 'gas_rc_value',
    # Add more if needed
}

# Buttons mapping for arm_safety, arm, cart, camera (example)
BUTTON_MAP = {
    310: 'arm_safety_rc_value',
    311: 'arm_rc_value',
    312: 'cart_rc_value',
    313: 'camera_rc_value',
    304: 'gear_shift_up',    # A button to gear up
    305: 'gear_shift_down',  # B button to gear down
    # Add more if needed
}

# For simplicity, toggle button channel between 1000 (released) and 2000 (pressed)
button_states = {
    310: 1000,
    311: 1000,
    312: 1000,
    313: 1000,
    304: 0,  # We'll treat gear buttons as momentary, not toggled
    305: 0,
}

def send_packet():
    packet = struct.pack(
        'HHHHHHHH',
        gear_rc_value,
        steering_rc_value,
        brake_rc_value,
        gas_rc_value,
        arm_safety_rc_value,
        arm_rc_value,
        cart_rc_value,
        camera_rc_value
    )
    sock.sendto(packet, (PI_IP, PI_PORT))
    print(f"Sent packet: gear={gear_rc_value}, steering={steering_rc_value}, brake={brake_rc_value}, gas={gas_rc_value}, arm_safety={arm_safety_rc_value}, arm={arm_rc_value}, cart={cart_rc_value}, camera={camera_rc_value}")

def gear_shift_up():
    global gear_rc_value
    gear_rc_value = 2000
    print(f"Gear shifted UP, gear_rc_value = {gear_rc_value}")

def gear_shift_down():
    global gear_rc_value
    gear_rc_value = 1000
    print(f"Gear shifted DOWN, gear_rc_value = {gear_rc_value}")

# Event reading loop
for event in device.read_loop():
    if event.type == ecodes.EV_ABS and event.code in AXIS_MAP:
        val = normalize_axis(event.value, invert=(event.code == 4))  # Invert gas
        var_name = AXIS_MAP[event.code]
        globals()[var_name] = val
        send_packet()

    elif event.type == ecodes.EV_KEY and event.code in BUTTON_MAP:
        var_name = BUTTON_MAP[event.code]
        if event.value == 1:  # pressed
            if var_name == 'gear_shift_up':
                gear_shift_up()
            elif var_name == 'gear_shift_down':
                gear_shift_down()
            else:
                button_states[event.code] = 2000
                globals()[var_name] = button_states[event.code]
        else:  # released
            if var_name not in ['gear_shift_up', 'gear_shift_down']:
                button_states[event.code] = 1000
                globals()[var_name] = button_states[event.code]
        send_packet()
