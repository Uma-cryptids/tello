import tkinter as tk
from djitellopy import tello
import math
import time


class Drone:
    MAX = 60
    TAU = -0.05
    DELTA = 0.05

    def __init__(self):
        self.speed = [0, 0, 0, 0]
        self.position = [0.0, 0.0, 0.0, 0.0]
        self.cnt = 0
        self.last = ""
        self.lasttime = time.time()
        self.flag = True
        self.liftoff = False
        # self.drone = drone
        # self.drone.connect()

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

            self.flag = True

            if key == "w":
                self.speed[0] = int(self.MAX*(1 - math.exp(self.TAU*self.cnt)))
            elif key == "s":
                self.speed[0] = int(self.MAX*(math.exp(self.TAU*self.cnt) - 1))
            elif key == "a":
                self.speed[1] = int(self.MAX*(math.exp(self.TAU*self.cnt) - 1))
            elif key == "d":
                self.speed[1] = int(self.MAX*(1 - math.exp(self.TAU*self.cnt)))
            elif key == "space":
                self.speed[2] = int(self.MAX*(1 - math.exp(self.TAU*self.cnt)))
            elif key == "x":
                self.speed[2] = int(self.MAX*(math.exp(self.TAU*self.cnt) - 1))
            elif key == "Right":
                self.speed[3] = int(self.MAX*(1 - math.exp(self.TAU*self.cnt)))
            elif key == "Left":
                self.speed[3] = int(self.MAX*(math.exp(self.TAU*self.cnt) - 1))

            self.position = list(
                map(lambda x, y: x+y*self.DELTA, self.position, self.speed))

            # self.drone.send_rc_control(*self.speed)

        self.last = key
        self.lasttime = time.time()
        self.cnt += 1

    def free(self):
        if self.flag:
            self.speed = [0, 0, 0, 0]
        else:
            self.flag = True

    def positionstr(self):
        return str(list(map(round, self.position, [2]*len(self.position))))

    def battery(self):
        return 100


class Operator(tk.Frame):
    def __init__(self, parent, drone):
        tk.Frame.__init__(self, parent, width=500, height=400)

        self.parent = parent
        self.tello = drone

        self.battery_label = tk.Label(
            self, text="battery: "+str(self.tello.battery()), width=50)
        self.battery_label.pack(fill="both", padx=10, pady=10)

        self.takeofflabel = tk.Label(self, text="landing", width=50)
        self.takeofflabel.pack(fill="both", padx=10, pady=10)

        self.speedlabel = tk.Label(self, text="speed: " +
                                   str(self.tello.speed), width=50)
        self.speedlabel.pack(fill="both", padx=10, pady=10)

        self.positionlabel = tk.Label(
            self, text="position: "+self.tello.positionstr(), width=50)
        self.positionlabel.pack(fill="both", padx=10, pady=10)

        self.speedlabel.bind("<KeyPress>", self.press)
        self.speedlabel.bind("<KeyRelease>", self.release)

        self.speedlabel.focus_set()
        self.speedlabel.bind("<1>", lambda event: self.speedlabel.focus_set())

    def press(self, event):
        self.tello.enter(event.keysym)
        if self.tello.liftoff:
            self.takeofflabel.configure(text="takeoff")
        else:
            self.takeofflabel.configure(text="landing")
        self.battery_label.configure(
            text="battery: "+str(self.tello.battery()))
        self.positionlabel.configure(text="position: "+self.tello.positionstr())
        self.speedlabel.configure(text="speed: "+str(self.tello.speed))

    def release(self, _event):
        self.tello.free()
        self.battery_label.configure(
            text="battery: "+str(self.tello.battery()))
        self.positionlabel.configure(text="position: "+self.tello.positionstr())
        self.speedlabel.configure(text="speed: "+str(self.tello.speed))


if __name__ == "__main__":
    root = tk.Tk()
    mytello = Drone()
    Operator(root, mytello).pack(fill="both", expand=True)
    root.mainloop()
