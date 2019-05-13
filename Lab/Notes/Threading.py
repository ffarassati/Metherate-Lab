#Your code update the cursor but it's only done after your busy process is terminated. So you can execute your busy #process in a thread to prevent the user interface to freeze.

import tkinter as tk
import threading

def worker():
    for x in range(0, 100000):
        print(x)
    root.config(cursor="arrow")

def button():
    root.config(cursor="watch")
    threading.Thread(target=worker).start() 

root = tk.Tk()
root.geometry("300x500")
root.config(cursor="arrow")

button_1 = tk.Button(master=root, command=button, width=10)
button_1.grid()

root.mainloop()
