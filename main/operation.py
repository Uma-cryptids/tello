import tkinter as tk
from math import exp, floor
import time


class Drone:
    MAX = 80
    TAU = -0.05
    KEY_CONFIG = {"w": 1, "a": 0, "s": 1, "d": 0,
                  "space": 2, "x": 2, "Right": 3, "Left": 3}
    NEG = {"s", "d", "x", "Left"}

    def __init__(self):  # , drone):
        self.speed = [0, 0, 0, 0]
        self.cnt = 0
        self.last = ""
        self.lasttime = time.time()
        self.liftoff = False
        # self.drone = drone
        # self.drone.connect()
        # self.drone.streamon()

    def speed_calc(self, t):
        return int(floor(self.MAX*(1-exp(self.TAU*t))))

    def enter(self, key: str):

        if key == "q":
            if not self.liftoff:
                # self.drone.takeoff()
                self.liftoff = True
            else:
                # self.drone.land()
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

            # self.drone.send_rc_control(*self.speed)

        self.last = key
        self.lasttime = time.time()
        self.cnt += 1

    def free(self):
        self.speed = [0, 0, 0, 0]
        # self.drone.send_rc_control(*self.speed)

    def get_battery(self):
        return 100

class Operator(tk.Frame):
    def __init__(self, parent, drone):
        tk.Frame.__init__(self, parent, width=500, height=400)

        self.parent = parent
        self.tello = drone

        self.batterylabel = tk.Label(self, text="battery: "+str(self.tello.get_battery())+"%", width=50)
        self.batterylabel.pack(fill="both", padx=10, pady=10)

        self.takeofflabel = tk.Label(self, text="landing", width=50)
        self.takeofflabel.pack(fill="both", padx=10, pady=10)

        self.detection_txt = str(0)+"-person detection"
        self.detection_label = tk.Label(self, text=self.detection_txt, width=50)
        self.detection_label.pack(fill="both", pady=10)

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
        self.batterylabel.configure(text="battery: "+str(self.tello.get_battery())+"%")
        self.label.configure(text="speed: "+str(self.tello.speed))

    def release(self, _event):
        self.tello.free()
        self.batterylabel.configure(text="battery: "+str(self.tello.get_battery())+"%")
        self.label.configure(text="speed: "+str(self.tello.speed))

if __name__ == "__main__":
    root = tk.Tk()
    mytello = Drone()#tello.Tello())
    Operator(root, mytello).pack(fill="both", expand=True)
    root.mainloop()