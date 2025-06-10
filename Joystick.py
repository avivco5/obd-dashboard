import pygame
import time

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()

# Ensure at least one joystick is connected
joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("No joystick detected.")
    exit(1)

# Use the first joystick (TX16S if it's first)
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Using joystick: {joystick.get_name()}")
print(f"Number of axes: {joystick.get_numaxes()}")

# Read axes in a loop
try:
    while True:
        pygame.event.pump()  # process internal pygame events

        axes = []
        for i in range(joystick.get_numaxes()):
            value = joystick.get_axis(i)
            axes.append(round(value, 3))

        print(f"Axes: {axes}")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting.")
finally:
    pygame.quit()
