from djitellopy import tello
from math import exp, floor
from threading import Thread
import cv2
from time import time
import tkinter as tk

SETTING_FILE = "Resources/haarcascade_frontalface_default.xml"


class face_detection:
    def __init__(self):
        self.detector = cv2.CascadeClassifier(SETTING_FILE)

    def detect(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(gray_img, 1.1, 4)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (60, 169, 181), 1)
        return (len(faces), img)

    def drone_detect(self):
        global drone
        return self.detect(drone.get_frame_read().frame)


class Drone_Contoroler:
    MAX = 80
    TAU = -0.05
    KEY_CONFIG = {"w": 1, "a": 0, "s": 1, "d": 0,
                  "space": 2, "x": 2, "Right": 3, "Left": 3}
    NEG = {"s", "a", "x", "Left"}

    def __init__(self):

        global drone
        drone.connect()
        drone.streamon()

        self.speed = [0.0, 0.0, 0.0, 0.0]
        self.cnt = 0
        self.last_input = ""
        self.last_time = time()
        self.liftoff = False

    def __str__(self):
        return "".join(str(round(self.speed[i], 2)) for i in range(len(self.speed)))

    def speed_calculate(self, t: int):
        return int(floor(self.MAX*(1-exp(self.TAU*t))))

    def enter(self, key: str):
        global drone
        if key == "q":
            if self.liftoff:
                drone.land()
                self.liftoff = False
            else:
                self.liftoff = True
                drone.takeoff()

        if self.liftoff:
            if key != self.last_input or time() - self.last_time > 0.1:
                self.cnt = 0

            if key in self.KEY_CONFIG.keys():
                id = self.KEY_CONFIG[key]
                if key not in self.NEG:
                    self.speed[id] = self.speed_calculate(self.cnt)
                else:
                    self.speed[id] = -self.speed_calculate(self.cnt)

            drone.send_rc_control(*self.speed)

        self.last_input = key
        self.last_time = time()
        self.cnt += 1

    def stop(self):
        global drone
        self.speed = [0, 0, 0, 0]
        drone.send_rc_control(*self.speed)

    @classmethod
    def get_battery(cls):
        global drone
        return drone.get_battery()


class Operator(tk.Frame):

    def __init__(self, parent, drone_contoroler: Drone_Contoroler):
        global img, dnum
        tk.Frame.__init__(self, parent, width=800, height=800)
        self.controler = drone_contoroler
        self.master.winfo_geometry("640x360")

        self.battery_txt = "battery: "+str(self.controler.get_battery())+"%"
        self.battery_label = tk.Label(self, text=self.battery_txt, width=50)
        self.battery_label.pack(fill="both", pady=10)

        self.detection_txt = str(dnum)+"-person detection"
        self.detection_label = tk.Label(self, text=self.battery_txt, width=50)
        self.detection_label.pack(fill="both", pady=10)

        self.takeoff_txt = "landing"
        self.takeoff_label = tk.Label(self, text=self.takeoff_txt, width=50)
        self.takeoff_label.pack(fill="both", pady=10)

        self.speed_txt = "speed: " + str(self.tello.speed)
        self.speed_label = tk.Label(self, text=self.speed_txt, width=50)
        self.speed_label.pack(fill="both", pady=10)

        self.speed_label.bind("<KeyPress>", self.press)
        self.speed_label.bind("<KeyRelease>", self.release)

        self.speed_label.focus_set()
        self.speed_label.bind("<1>", lambda event: self.label.focus_set())

    def press(self, event):
        global dnum

        self.controler.enter(event.keysym)

        if self.controler.liftoff:
            self.takeoff_txt = "takeoff"
        else:
            self.takeoff_txt = "landing"
        self.takeoff_label.configure(text=self.takeoff_label)

        self.battery_txt = "battery: "+str(self.controler.get_battery())+"%"
        self.battery_label.configure(text=self.battery_txt)

        self.speed_txt = "speed: "+str(self.controler)
        self.speed_label.configure(text=self.speed_txt)

        self.detection_txt = str(dnum)+"-person detection"
        self.detection_label.configure(text=self.detection_txt)

    def release(self, _event):
        global dnum

        self.controler.free()

        self.battery_txt = "battery: "+str(self.controler.get_battery())+"%"
        self.battery_label.configure(text=self.battery_txt)

        self.speed_txt = "speed: "+str(self.controler)
        self.speed_label.configure(text=self.speed_txt)

        self.detection_txt = str(dnum)+"-person detection"
        self.detection_label.configure(text=self.detection_txt)


def detection(detect_drone):
    global stop, dnum
    detector = face_detection()
    detector.set_drone(detect_drone)
    while True:
        dnum, img = detector.drone_detect()
        cv2.imshow("Result", img)
        cv2.waitKey(1)
        if stop:
            break


if __name__ == "__main__":
    global stop, drone, dnum
    stop = False
    drone = tello.Tello()
    dnum = 0
    root = tk.Tk()
    drone_contoroler = Drone_Contoroler()
    drone.streamon()
    Operator(root).pack(fill="both", expand=True)
    thread1 = Thread(target=detection)
    thread1.start()

    root.mainloop()

    stop = True
    drone.streamoff()
