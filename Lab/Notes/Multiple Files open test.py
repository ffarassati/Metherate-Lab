from tkinter import *
from tkinter import filedialog


root = Tk()
filez = filedialog.askopenfilenames(parent=root,title='Choose a file')
print(root.splitlist(filez))
