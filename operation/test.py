import tkinter as tk


class test_frame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=400,  height=400)

        self.label = tk.Label(self, text="", width=20)
        self.label.pack(fill="both", padx=100, pady=100)

        self.label.bind("<KeyPress>", self.press)
        self.label.bind("<KeyRelease>", self.release)
        
        self.label.focus_set()
        self.label.bind("<1>", lambda event: self.label.focus_set())

    def press(self, event):
        self.label.configure(text="press :"+event.keysym)

    def release(self, event):
        self.label.configure(text="release :"+event.keysym)


if __name__ == "__main__":
    root = tk.Tk()
    test_frame(root).pack(fill="both", expand=True)
    root.mainloop()
