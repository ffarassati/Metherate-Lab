from tkinter import *
from tkinter import filedialog

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


root = Tk()
root.wm_title("Embedding in Tk")
root.geometry("500x500")
root.resizable(False, False)

fig = Figure(figsize=(5, 4), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

def _quit():
    root.quit()     
    root.destroy()  
                    

def _plot():
    root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Open", \
                                                filetypes = (("AXGR Files","*.axgr"), ("ATF Files","*.atf"),("All Files","*.*")))
    fig = Figure(figsize=(5, 4), dpi=100)
    a = fig.add_subplot(111)
    a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
    
    global canvas
    canvas.get_tk_widget().pack_forget()
    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)


button = Button(master=root, text="Quit", command=_quit)
button2 = Button(master=root, text="Plot", command= _plot)
button2.pack(side=BOTTOM)
button.pack(side=BOTTOM)

mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.
