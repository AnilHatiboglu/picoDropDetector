import tkinter as tk
from PIL import ImageTk, Image
import recordedRun
import cv2
import os
     
class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)     
        vars = {}
        files = os.listdir()
        self.lbox = tk.Listbox(self)

        self.checkCmd = tk.IntVar(self)
        self.checkCmd.set(0)

        self.lbox.grid(column=1)
        for item in files:
            if item.endswith(".avi"):
                self.lbox.insert(tk.END,item)

        filename = self.lbox.bind('<<ListboxSelect>>',self.getInput)
        print(filename)

        tk.Label(self, text = "Max Radius").grid(row = 1, column = 1, sticky = tk.W)
        tk.Label(self, text = "Min Radius").grid(row = 2, column = 1, sticky = tk.W)

        self.Rmax = tk.Entry()
        self.Rmin = tk.Entry()

        self.Rmax.grid(row = 1, column = 2)
        self.Rmin.grid(row = 2, column = 2)

        c = tk.Checkbutton(self, text="Do you want to cancel video?", variable=self.checkCmd, onvalue=1, offvalue=0)
        c.grid(columnspan=3)

        tk.Button(self, text = "submit", command = self.getInput).grid(row = 4, sticky = tk.W)
    
    def getInput(self):
        value = self.lbox.get(tk.ANCHOR)
        a = self.Rmax.get()
        b = self.Rmin.get()
        c = self.checkCmd.get() 
        
        print("video "+value+" will be opened...")

        r = recordedRun.player(value,b,a,c)
app = SampleApp()
app.mainloop()
