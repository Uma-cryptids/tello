import keyboard
from djitellopy import tello
from time import sleep
import cv2


class key_controle:
    S = 40
    SPEED = {"w": (0, S, 0, 0),
             "a": (-S, 0, 0, 0),
             "s": (0, -S, 0, 0),
             "d": (S, 0, 0, 0),
             "shift": (0, 0, -S, 0),
             "space": (0, 0, S, 0)}

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
drone.streamon()
print(drone.get_battery())

drone.takeoff()

while True:
    img = drone.get_frame_read().frame
    img = cv2.resize(img, (360, 240))
    cv2.imshow("Image", img)
    try:
        movement = key.get_key()
        drone.send_rc_control(*movement)
        print(movement)
    except:
        break
    sleep(0.1)
drone.land()
