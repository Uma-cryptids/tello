from djitellopy import tello
from math import exp, floor
from threading import Thread
import cv2
from time import time
import tkinter as tk

# weight file for neural network of face detection
SETTING_FILE = "Resources/haarcascade_frontalface_default.xml"


class Face_Detection:
    '''
    Face Detection class
    Valiable
    - detector  :: opencv Cascade Classifier, should be private
    - drone     :: global, tello.Tello()

    Function
    - __init__ ()   :: initializer, need to import opencv
    - detect(img)   :: face detection, argument is CV image type
    - drone_detect():: face detection with image from drone, need to global tello variable
    '''

    def __init__(self):
        self.detector = cv2.CascadeClassifier(SETTING_FILE)

    def detect(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(gray_img, 1.1, 4)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (60, 169, 181), 1)
        return (len(faces), img)

    def drone_detect(self):
        global DRONE
        return self.detect(DRONE.get_frame_read().frame)


class Drone_Contoroler:
    '''
    Drone Controloer Class
    Constant
    - MAX        :: maximum speed
    - TAU        :: intensity of velocity
    - KEY_CONFIG :: key map to velocity vector index
    - NEG        :: flag to inverse velocity

    Valiable
    - speed      :: velocity vector
    - cnt        :: access counter to calculate velocity
    - last_input :: to detecet consequtive inputs
    - last_time  :: to detecet consequtive inputs
    - liftoff    :: whether the drone lift off now

    Function
    - __init__        :: initializer, need to global tello variable
    - speed_calculate :: calculate speed from "cnt", 1 - exp(t)
    - enter           :: operate drone from key push
    - stop            :: stop drone movement
    - get_battery     :: return the remaining power of drone
    '''
    MAX = 80
    TAU = -0.05
    KEY_CONFIG = {"w": 1, "a": 0, "s": 1, "d": 0,
                  "space": 2, "x": 2, "Right": 3, "Left": 3}
    NEG = {"s", "a", "x", "Left"}

    def __init__(self):

        global DRONE
        DRONE.connect()
        DRONE.streamon()

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
        global DRONE
        if key == "q":
            if self.liftoff:
                DRONE.land()
                self.liftoff = False
            else:
                self.liftoff = True
                DRONE.takeoff()

        if self.liftoff:
            if key != self.last_input or time() - self.last_time > 0.1:
                self.cnt = 0

            if key in self.KEY_CONFIG.keys():
                id = self.KEY_CONFIG[key]
                if key not in self.NEG:
                    self.speed[id] = self.speed_calculate(self.cnt)
                else:
                    self.speed[id] = -self.speed_calculate(self.cnt)

            DRONE.send_rc_control(*self.speed)

        self.last_input = key
        self.last_time = time()
        self.cnt += 1

    def stop(self):
        global DRONE
        self.speed = [0, 0, 0, 0]
        DRONE.send_rc_control(*self.speed)

    @classmethod
    def get_battery(cls):
        global DRONE
        return DRONE.get_battery()


class Operator(tk.Frame):
    '''
    Operator : class managing GUI
    '''

    def __init__(self, parent, drone_contoroler: Drone_Contoroler):
        global DNUM
        tk.Frame.__init__(self, parent, width=800, height=800)
        self.controler = drone_contoroler
        self.master.winfo_geometry("640x360")

        self.battery_txt = "battery: "+str(self.controler.get_battery())+"%"
        self.battery_label = tk.Label(self, text=self.battery_txt, width=50)
        self.battery_label.pack(fill="both", pady=10)

        self.detection_txt = str(DNUM)+"-person detection"
        self.detection_label = tk.Label(self, text=self.detection_txt, width=50)
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
        global DNUM

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

        self.detection_txt = str(DNUM)+"-person detection"
        self.detection_label.configure(text=self.detection_txt)

    def release(self, _event):
        global DNUM

        self.controler.free()

        self.battery_txt = "battery: "+str(self.controler.get_battery())+"%"
        self.battery_label.configure(text=self.battery_txt)

        self.speed_txt = "speed: "+str(self.controler)
        self.speed_label.configure(text=self.speed_txt)

        self.detection_txt = str(DNUM)+"-person detection"
        self.detection_label.configure(text=self.detection_txt)


def detection(detect_drone):
    '''
    for threading
    '''
    global STOP, DNUM
    detector = Face_Detection()
    detector.set_drone(detect_drone)
    while True:
        DNUM, img = detector.drone_detect()
        cv2.imshow("Result", img)
        cv2.waitKey(1)
        if STOP:
            break


if __name__ == "__main__":
    global STOP, DRONE, DNUM
    STOP = False
    DRONE = tello.Tello()
    DNUM = 0
    root = tk.Tk()
    drone_contoroler = Drone_Contoroler()
    DRONE.streamon()
    Operator(root).pack(fill="both", expand=True)
    thread1 = Thread(target=detection)
    thread1.start()

    root.mainloop()

    STOP = True
    DRONE.streamoff()
