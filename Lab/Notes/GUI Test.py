import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk


def load():
    print("Load")
    
def save():
    print("Save")

win = tk.Tk()
win.title('Text Editor')
win.geometry('500x500')


openBtn = tk.Button(win, text='Open', command=load)
openBtn.pack(expand=tk.FALSE, fill=tk.X, side=tk.TOP)

saveBtn = tk.Button(win, text='Save', command=save)
saveBtn.pack(expand=tk.FALSE, fill=tk.X, side=tk.TOP)

win.mainloop()
