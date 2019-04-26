from tkinter import *

def func(event):
   link['state'] = DISABLED
   print(link.get())
    
def callback(event):
    link['state'] = NORMAL
    link.bind('<Return>', func)

root = Tk()
link = Entry(root, state=DISABLED)
link.pack()
link.bind("<Button-1>", lambda x: [print(50), print(10)])

cunt = Entry(root)
cunt.pack()


root.mainloop()
