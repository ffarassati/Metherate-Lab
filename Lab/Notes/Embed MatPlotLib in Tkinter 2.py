# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/	


# https://pythonprogramming.net/how-to-embed-matplotlib-graph-tkinter-gui/


import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter
from tkinter import ttk


LARGE_FONT= ("Verdana", 12)


class SeaofBTCapp(tkinter.Tk):

    def __init__(self, *args, **kwargs):
        
        tkinter.Tk.__init__(self, *args, **kwargs)

        tkinter.Tk.iconbitmap(self, default="")
        tkinter.Tk.wm_title(self, "Sea of BTC client")
        
        
        container = tkinter.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}


        frame = StartPage(container, self)
        self.frames[StartPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

        
class StartPage(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self,parent)
        label = tkinter.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)
        a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        button = ttk.Button(self, text="Plot", command= lambda: print(1))
                            
        button.pack(expand=tkinter.FALSE, fill=tkinter.X, side=tkinter.TOP)



app = SeaofBTCapp()
app.mainloop()
