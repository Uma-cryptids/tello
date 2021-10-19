import keyboard
from djitellopy import tello
from time import sleep


class key_controle:

    SPEED = {"w": (0, 10, 0, 0),
             "a": (10, 0, 0, 0),
             "s": (0, -10, 0, 0),
             "d": (-10, 0, 0, 0),
             "shift": (0, 0, -10, 0),
             "space": (0, 0, 10, 0)}

    def __init__(self):
        return

    def get_key(self):
        key = keyboard.read_key()
        if key in ["w", "a", "s", "d", "space", "shift"]:
            return self.SPEED[key]
        elif key == "esc":
            raise("Stop")
        else:
            return (0, 0, 0, 0)


drone = tello.Tello()
drone.connect()
key = key_controle()
drone.takeoff()
while True:
    try:
        movement = key.get_key()
        drone.send_rc_control(movement)
    except:
        break
    sleep(0.1)
drone.land()
