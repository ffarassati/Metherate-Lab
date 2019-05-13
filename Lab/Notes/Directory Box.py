import datetime
import os
import sys
from pathlib import Path
import traceback

from tkinter import *
from tkinter import filedialog
import tkinter.ttk as ttk
def directoryBox(title=None):
        #topLevel.update_idletasks()
        options = {}
        options['initialdir'] = os.path.dirname(os.path.realpath(__file__))
        options['title'] = title
        options['mustexist'] = False
        fileName = filedialog.askdirectory(**options)
        if fileName == "":
            return None
        else:
            return fileName 

directoryBox()
