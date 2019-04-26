import tkinter as tk

root = tk.Tk()
root.geometry("300x200")

def func(event):
    print("You hit return.")




def onclick():
    root.bind('<Return>', func)

button = tk.Button(root, text="click me", command=onclick)
button.pack()

root.mainloop()
