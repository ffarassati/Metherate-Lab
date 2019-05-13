import tkinter as tk
from tkinter import messagebox

root= tk.Tk() # create window

canvas1 = tk.Canvas(root, width = 800, height = 350)
canvas1.pack()


def ExitApplication():
    MsgBox = tk.messagebox.askquestion ('Exit Application','Are you sure you want to exit the application')
    if MsgBox == 'yes':
       root.destroy()
    else:
        tk.messagebox.showinfo('Return','You will now return to the application screen')
        
      
button1 = tk.Button (root, text='Exit Application',command=ExitApplication)
canvas1.create_window(97, 270, window=button1)
  
  
root.mainloop()
