from djitellopy import tello
import threading
import tkinter as tk
import cv2
from math import exp, floor
import time


class face_detection:
    def __init__(self):
        self.detector = cv2.CascadeClassifier(
            "Resources/haarcascade_frontalface_default.xml")
        self.drone = None

    def set_drone(self, drone):
        self.drone = drone

    def detect(self, img):
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.faces = self.detector.detectMultiScale(imgGray, 1.1, 4)
        for (x, y, w, h) in self.faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        return (len(self.faces), img)

    def drone_detect(self):
        return self.detect(self.drone.drone.get_frame_read().frame)


class Drone:
    MAX = 80
    TAU = -0.05
    KEY_CONFIG = {"w": 1, "a": 0, "s": 1, "d": 0,
                  "space": 2, "x": 2, "Right": 3, "Left": 3}
    NEG = {"s", "a", "x", "Left"}

    def __init__(self, drone):
        self.speed = [0, 0, 0, 0]
        self.cnt = 0
        self.last = ""
        self.lasttime = time.time()
        self.liftoff = False
        self.drone = drone
        self.drone.connect()
        self.drone.streamon()

    def speed_calc(self, t):
        return int(floor(self.MAX*(1-exp(self.TAU*t))))

    def enter(self, key: str):
        if key == "q":
            if not self.liftoff:
                flag = True
                self.drone.takeoff()
                self.liftoff = True
            else:
                flag = False
                self.drone.land()
                self.liftoff = False

        if self.liftoff:
            if key != self.last:
                self.cnt = 0

            if time.time() - self.lasttime > 0.2:
                self.cnt = 0

            self.flag = False

            if key in self.KEY_CONFIG.keys():
                if key not in self.NEG:
                    self.speed[self.KEY_CONFIG[key]
                               ] = self.speed_calc(self.cnt)
                else:
                    self.speed[self.KEY_CONFIG[key]
                               ] = -self.speed_calc(self.cnt)
            if key == "r":
                self.free()

            self.drone.send_rc_control(*self.speed)

        self.last = key
        self.lasttime = time.time()
        self.cnt += 1

    def free(self):
        self.speed = [0, 0, 0, 0]
        self.drone.send_rc_control(*self.speed)

    def get_battery(self):
        return self.drone.get_battery()


class Operator(tk.Frame):
    def __init__(self, parent, drone):
        tk.Frame.__init__(self, parent, width=500, height=400)

        self.parent = parent
        self.tello = drone

        self.batterylabel = tk.Label(
            self, text="battery: "+str(self.tello.get_battery())+"%", width=50)
        self.batterylabel.pack(fill="both", padx=10, pady=10)

        self.takeofflabel = tk.Label(self, text="landing", width=50)
        self.takeofflabel.pack(fill="both", padx=10, pady=10)

        self.label = tk.Label(self, text="speed: " +
                              str(self.tello.speed), width=50)
        self.label.pack(fill="both", padx=10, pady=10)

        self.label.bind("<KeyPress>", self.press)
        self.label.bind("<KeyRelease>", self.release)

        self.label.focus_set()
        self.label.bind("<1>", lambda event: self.label.focus_set())

    def press(self, event):
        self.tello.enter(event.keysym)
        if self.tello.liftoff:
            self.takeofflabel.configure(text="takeoff")
        else:
            self.takeofflabel.configure(text="landing")
        self.batterylabel.configure(
            text="battery: "+str(self.tello.get_battery())+"%")
        self.label.configure(text="speed: "+str(self.tello.speed))

    def release(self, _event):
        self.tello.free()
        self.batterylabel.configure(
            text="battery: "+str(self.tello.get_battery())+"%")
        self.label.configure(text="speed: "+str(self.tello.speed))


def detection(detect_drone):
    global stop
    detector = face_detection()
    detector.set_drone(detect_drone)
    while True:
        nop, img = detector.drone_detect()
        cv2.imshow("Result", img)
        cv2.waitKey(1)
        if stop:
            break


if __name__ == "__main__":
    global stop 
    stop = False
    tello_access = tello.Tello()
    root = tk.Tk()
    drone = Drone(tello_access)
    drone.drone.streamon()
    Operator(root, drone).pack(fill="both", expand=True)
    thread1 = threading.Thread(target=detection, args=(drone,))
    thread1.start()
    root.mainloop()
    stop = True
    drone.drone.streamoff()
