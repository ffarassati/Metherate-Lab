import tkinter as tk
import tkinter.ttk as ttk


def on_select(event):
    print(cb.get())
    

root = tk.Tk()

cb = ttk.Combobox(root, values=("1", "2", "3", "4", "5"))
cb.set("1")
cb.pack()
cb.bind('<<ComboboxSelected>>', on_select)


root.mainloop()
