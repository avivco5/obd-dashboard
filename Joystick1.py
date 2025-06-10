import pygame
import time

# Init pygame
pygame.init()
pygame.joystick.init()

# Check for connected joystick
if pygame.joystick.get_count() == 0:
    print("No joystick detected.")
    exit(1)

# Init joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()


print(f"Using joystick: {joystick.get_name()}")
num_axes = joystick.get_numaxes()
print(f"Number of axes: {num_axes}")
time.sleep(3)

# Main loop
try:
    while True:
        pygame.event.pump()  # Update internal state

        axis_strings = []
        for i in range(num_axes):
            value = joystick.get_axis(i)
            axis_strings.append(f"Axis {i}: {value:.3f}")

        print(" | ".join(axis_strings))
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopped.")
finally:
    pygame.quit()
