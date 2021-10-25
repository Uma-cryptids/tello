import tkinter as tk


class tello_operation:

    ADD_SPEED = 10

    def __init__(self):
        self.position = [0, 0, 0, 0]
        self.speed = [0, 0, 0, 0]

    def enter(self, key: str):
        add = [0, 0, 0, 0]
        if key == "w":
            add[1] = self.ADD_SPEED
        elif key == "a":
            add[1] = -self.ADD_SPEED
        elif key == "s":
            add = [-self.ADD_SPEED, 0, 0, 0]
        elif key == "d":
            add = [0, self.ADD_SPEED, 0, 0]
        elif key == "Shift_L":
            add = [0, 0, -self.ADD_SPEED, 0]
        elif key == "space":
            add = [0, 0, self.ADD_SPEED, 0]
        self.speed = tuple(map(lambda x, y: x+y, self.speed, add))


class Graphic(tk.Frame):
    def __init__(self, parent, drone):
        tk.Frame.__init__(self, parent, width=400,  height=400)

        self.label = tk.Label(self, text="press key", width=20)
        self.label.pack(fill="both", padx=100, pady=100)

        self.label.bind("<w>", self.on_wasd)
        self.label.bind("<a>", self.on_wasd)
        self.label.bind("<s>", self.on_wasd)
        self.label.bind("<d>", self.on_wasd)
        self.label.bind("<Shift-Key>", self.on_wasd)
        self.label.bind("<space>", self.on_wasd)

        # give keyboard focus to the label by default, and whenever
        # the user clicks on it
        self.label.focus_set()
        self.label.bind("<1>", lambda event: self.label.focus_set())

        self.tello = drone

    def on_wasd(self, event):
        self.tello.enter(event.keysym)
        self.label.configure(text="speed: " + str(self.tello.speed))


if __name__ == "__main__":
    root = tk.Tk()
    mytello = tello_operation()
    Graphic(root, mytello).pack(fill="both", expand=True)
    root.mainloop()
