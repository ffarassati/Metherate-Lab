from tkinter import *

OPTIONS = [
".txt",
] #etc

variable = StringVar(root)
variable.set(OPTIONS[0]) # default value

def ok(value):
    print ("value is:" + str(value))

w = OptionMenu(root, variable, *OPTIONS, command=ok)
w.pack()


mainloop()
