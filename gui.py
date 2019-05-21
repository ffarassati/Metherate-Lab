import datetime
import os
import sys
import subprocess
from pathlib import Path
import traceback
import axographio
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter.ttk as ttk
import xlsxwriter
from functools import partial
#import matplotlib
#import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
#from matplotlib.backend_bases import key_press_handler
#from matplotlib.figure import Figure
#matplotlib.use("TkAgg")
from processor import DataProcessor
import threading


# GLOBAL: SLASH
SLASH = "/"
if (sys.platform == 'win32'): # 'win32', 'darwin', 'linux'
    print(__file__, "running on Windows.")
    SLASH = "\\";
elif (sys.platform == 'darwin'):
    print(__file__, "running on Mac.")
    SLASH = "/";

# CONFIG FILE?
GRAPH = False
PERCENTAGE1 = .3
PERCENTAGE2 = .3333333
STD = 3
INITIALPLUS = 5
MAXPLUS = 25
STARTINGDIRECTORY = ""



# Static Functions
def changeState(TextEntry):
    TextEntry['state'] = NORMAL

def getFileExt(path):
    # Returns the file extension (i.e. '.atf') from any file path string
    return(path[path.rfind('.'):])

def changeWhenHovered(widget, color, event):
    if (widget['text'] != "(Entire Directory)"):
        widget["fg"] = color
        widget["cursor"] = "hand2"

def openFile(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])

class DataProcessorGUI:    

    def __init__(self, name="Data Processor (version 4)"):
    
        # GUI - Root 
        self.root = Tk()
        self.root.wm_title(name)
        #self.root.geometry("500x550") if GRAPH == True else self.root.geometry("500x290")
        self.root.resizable(False, False)
       
        # Default Values / State
        self.Name = name
        self.OutputFileType = ".xlsx"
        self.OutputFileName = ""
        self.InputFileName = ""
        self.Canvas = "None"
        self.Directory = ""
        self.DefaultDirectory = self.root
        self.OutputDirectory = str(self.root)

        # Taskbar Row
        if (True):
            # Taskbar - Frame
            self.taskbar = Frame(self.root)
            self.taskbar.columnconfigure(0, weight=1)
            self.taskbar.columnconfigure(1, weight=1)
            self.taskbar.columnconfigure(2, weight=9)
            self.taskbar.columnconfigure(3, weight=1)
            self.taskbar.columnconfigure(4, weight=1)
            self.taskbar.columnconfigure(5, weight=1)
            self.taskbar.columnconfigure(6, weight=1)

            # Taskbar - Content
            openfile = Button(master=self.taskbar, text="Choose File", command=self.OpenFile, width = 9)
            openfile.grid(row=0, column=0, sticky=W+E, padx=5)
            openfile['state'] = NORMAL
            
            openfolder = Button(master=self.taskbar, text="Choose Folder", command=self.OpenDir, width = 11)
            openfolder.grid(row=0, column=1, sticky=W+E, padx=0)
            openfolder['state'] = NORMAL
            
            exporttext = Label(self.taskbar, text="Export as:")
            exporttext.grid(row=0, column=3, sticky=E)
            
            self.ComboBox = ttk.Combobox(self.taskbar, values=(".txt", ".xlsx"), width = 4) # .xlsx support coming soon
            self.ComboBox.set(self.OutputFileType)
            self.ComboBox.grid(row=0, column=4, sticky=W+E)
            self.ComboBox.bind('<<ComboboxSelected>>', self.SelectOutputType)

            self.export = Button(master=self.taskbar, text="Process and Export")
            self.export.grid(row=0, column=5, sticky=W+E, padx=3)
            self.export['state'] = DISABLED

            self.view = Button(master=self.taskbar, text="View", width = 5)
            self.view.grid(row=0, column=6, sticky=W+E, padx=3)
            self.view['state'] = DISABLED
            
            self.taskbar.pack(fill = X, pady = (5,0))

        # Settings Section 1
        if (True):
            # Border
            self.border = Frame(self.root, bg = "gray", height = 1)
            self.border.pack(fill = X, pady = 10)
            
            # File Names
            self.files = Frame(self.root)
            self.files.columnconfigure(0, weight = 1)
            self.files.columnconfigure(1, weight = 20)
            
            self.FileName = Label(self.files, text="File: ", padx = 2, pady = 3)
            self.FileName.grid(row=1, column=0, sticky=W)
            
            self.inputtext = Label(self.files, text="")
            self.inputtext.grid(row=1, column=1, sticky=W)
            self.inputtext.bind("<Enter>", partial(changeWhenHovered, self.inputtext, "blue"))
            self.inputtext.bind("<Leave>", partial(changeWhenHovered, self.inputtext, "black"))
            
            self.FolderName = Label(self.files, text="Folder: ", padx = 2, pady = 3)
            self.FolderName.grid(row=2, column=0, sticky=W)
            
            self.srctext = Label(self.files, text="")
            self.srctext.grid(row=2, column=1, sticky=W)
            self.srctext.bind("<Button-1>", lambda e: openFile(self.srctext["text"]))
            self.srctext.bind("<Enter>", partial(changeWhenHovered, self.srctext, "blue"))
            self.srctext.bind("<Leave>", partial(changeWhenHovered, self.srctext, "black"))
            
            self.files.pack(fill = X, padx = 8, pady = (0, 10))
            
        # Settings Section 2
        if (True):
            # Settings Row 1 - Frame      
            self.sr2 = Frame(self.root)
            self.sr2.columnconfigure(0, weight=1)
            self.sr2.columnconfigure(1, weight=2)
            self.sr2.columnconfigure(2, weight=2)
            self.sr2.columnconfigure(3, weight=2)
            self.sr2.columnconfigure(4, weight=2)
            self.sr2.columnconfigure(5, weight=2)
            self.sr2.columnconfigure(6, weight=2)
            self.sr2.columnconfigure(7, weight=2)
            self.sr2.columnconfigure(8, weight=2)
            self.sr2.columnconfigure(9, weight=2)
            self.sr2.columnconfigure(10, weight=2)

            # Settings Row 1 - Titles
            self.BaselineTitle = Label(self.sr2, text="Baseline", padx = 3, pady = 3, borderwidth=2, relief="groove")
            self.BaselineTitle.grid(row=0, column=1, sticky=W+E)
            self.OnsetTitle = Label(self.sr2,  text="Onset Latency", padx = 3, pady = 3, borderwidth=2, relief="groove")
            self.OnsetTitle.grid(row=1, column=1, sticky=W+E)
            self.InitialPeakTitle = Label(self.sr2,  text="Initial Peak", padx = 3, pady = 3, borderwidth=2, relief="groove")
            self.InitialPeakTitle.grid(row=2, column=1, sticky=W+E)
            self.MaxPeakTitle = Label(self.sr2,  text="Max Peak", padx = 3, pady = 3, borderwidth=2, relief="groove")
            self.MaxPeakTitle.grid(row=3, column=1, sticky=W+E)
            self.MaxSlopeTitle = Label(self.sr2,  text="Initial Max Slope", padx = 3, pady = 3, borderwidth=2, relief="groove")
            self.MaxSlopeTitle.grid(row=4, column=1, sticky=W+E)
                        
            # 1) Baseline            
            self.BaselineStartLabel = Label(self.sr2, text="         From: ", pady = 3)
            self.BaselineStartLabel.grid(row=0, column=2, sticky=E)
            self.BaselineStartField = Entry(self.sr2, width = 6)
            self.BaselineStartField['state'] = DISABLED
            self.BaselineStartField.grid(row=0, column=3, sticky=W)

            self.BaselineEndLabel = Label(self.sr2, text="To: ",  pady = 3)
            self.BaselineEndLabel.grid(row=0, column=4, sticky=E)
            self.BaselineEndField = Entry(self.sr2, width = 6)
            self.BaselineEndField['state'] = DISABLED
            self.BaselineEndField.grid(row=0, column=5, sticky=W)

            # 2) Onset
            self.OnsetStartLabel = Label(self.sr2, text="       From: ", pady = 3)
            self.OnsetStartLabel.grid(row=1, column=2, sticky=E)
            self.OnsetStartField = Entry(self.sr2, width = 6)
            self.OnsetStartField['state'] = DISABLED
            self.OnsetStartField.grid(row=1, column=3, sticky=W)

            self.OnsetEndLabel = Label(self.sr2, text="To: ",  pady = 3)
            self.OnsetEndLabel.grid(row=1, column=4, sticky=E)
            self.OnsetEndField = Entry(self.sr2, width = 6)
            self.OnsetEndField['state'] = DISABLED
            self.OnsetEndField.grid(row=1, column=5, sticky=W)
            
            self.StdDevLabel = Label(self.sr2, text="Std. Deviation x ", pady = 3)
            self.StdDevLabel.grid(row=1, column=6, sticky=E)
            self.StdDevField = Entry(self.sr2, width = 6)
            self.StdDevField['state'] = DISABLED
            self.StdDevField.grid(row=1, column=7, sticky=W)
            
            # 3) Initial Peak
            self.InitialPeakLabel1 = Label(self.sr2, text="Onset (ms)", pady = 3)
            self.InitialPeakLabel1.grid(row=2, column=3, sticky=E)
            self.InitialPeakLabel2 = Label(self.sr2, text="+ ", pady = 3)
            self.InitialPeakLabel2.grid(row=2, column=4, sticky=W+E)
            self.InitialPeakField = Entry(self.sr2, width = 6)
            self.InitialPeakField['state'] = DISABLED
            self.InitialPeakField.grid(row=2, column=5, sticky=W)

            # 3) Max Peak
            self.MaxPeakLabel1 = Label(self.sr2, text="Onset (ms)", pady = 3)
            self.MaxPeakLabel1.grid(row=3, column=3, sticky=E)
            self.MaxPeakLabel2 = Label(self.sr2, text="+ ", pady = 3)
            self.MaxPeakLabel2.grid(row=3, column=4, sticky=W+E)
            self.MaxPeakField = Entry(self.sr2, width = 6)
            self.MaxPeakField['state'] = DISABLED
            self.MaxPeakField.grid(row=3, column=5, sticky=W)
            
            # 3) Initial Max Slope
            self.MaxSlopeLabel1 = Label(self.sr2, text="Onset (ms)", pady = 3)
            self.MaxSlopeLabel1.grid(row=4, column=3, sticky=E)
            self.MaxSlopeLabel2 = Label(self.sr2, text="+ ", pady = 3)
            self.MaxSlopeLabel2.grid(row=4, column=4, sticky=W+E)
            self.MaxSlopeField = Entry(self.sr2, width = 6)
            self.MaxSlopeField['state'] = DISABLED
            self.MaxSlopeField.grid(row=4, column=5, sticky=W)
            
            self.RegressionLabel = Label(self.sr2, text="Regression Points: ", pady = 3)
            self.RegressionLabel.grid(row=4, column=6, sticky=E)
            self.RegressionField = Entry(self.sr2, width = 6)
            self.RegressionField['state'] = DISABLED
            self.RegressionField.grid(row=4, column=7, sticky=W)
            
            self.sr2.pack(fill = X, pady = (10, 5), padx = 8)

        # Output Row
        if (True):
            # Output - Frame
            self.output = Frame(self.root, borderwidth = 1, relief = "groove")
            self.output.columnconfigure(0, weight=1)
            
            # Output - Content
            self.consoletext = Label(self.output, text="", padx = 0, pady = 3, fg="black", font=("TkDefaultFont", 8))
            self.consoletext.grid(row=0, column=0, sticky=W+E) 

            self.output.pack(fill = X, pady = (7, 0))   
       
        # Graph
        if (GRAPH == True):
            self.graph = Frame(self.root) 
            self.graph.pack(fill = X, side = BOTTOM)
            self.clearGraph()
        
        mainloop()
    
    def GUIPrint(self, string):
        self.consoletext['text'] = string
        
    def showGraph(self, file_name, inputfile):
        
        self.Canvas.get_tk_widget().pack_forget()
        
        fig = Figure(figsize=(5, 4), dpi=100)
        plt = fig.add_subplot(111)
        x = inputfile.data[0]
        for i in range(14):
            plt.plot(x, inputfile.data[i+1])

        self.Canvas = FigureCanvasTkAgg(fig, master=self.graph)
        self.Canvas.draw()
        self.Canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        Toolbar = NavigationToolbar2Tk(self.Canvas, self.graph)

    def clearGraph(self):
    
        if (self.Canvas != "None"):
            self.Canvas.destroy()
            
        fig = Figure(figsize=(2, 4), dpi=100)
        self.Canvas = FigureCanvasTkAgg(fig, master=self.graph)
        self.Canvas.draw()
        self.Canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    def OpenFile(self):
        
        if (self.DefaultDirectory == self.root) or (Path(self.DefaultDirectory).is_dir() == False):
            self.DefaultDirectory = self.root
            
        self.root.filename = filedialog.askopenfilename(initialdir = self.DefaultDirectory, title = "Choose single file to process", filetypes = (("AXGR Files","*.axgr"), ("ATF Files","*.atf"))) # Pop-up window to choose a file to process  
        if (getFileExt(self.root.filename) != ".axgr") and (getFileExt(self.root.filename) != ".atf"):
            return False # end the function if they pressed cancel


        self.DefaultDirectory = self.root.filename[:self.root.filename.rfind("/")] # Remember this file directory
        self.InputFileName = self.root.filename
        self.Processor = DataProcessor()
        
        self.inputtext['text'] = self.InputFileName[self.InputFileName.rfind('/')+1:] # change input file text to the current file"
        self.inputtext.bind("<Button-1>", lambda e: openFile(self.InputFileName))
        self.srctext['text'] = self.DefaultDirectory
        self.GUIPrint("") # clear console

        try:
            self.Processor.Extract(self.root.filename)
            if GRAPH == True:
                self.showGraph(self.root.filename, self.Processor.getAxographFile()) if (self.Processor.isGraphable()) else self.clearGraph()   
        except Exception as e:
            traceback.print_exc()
            self.GUIPrint("Error in processing " + self.InputFileName[self.InputFileName.rfind('/')+1:])
            return False
        
        self.export['state'] = NORMAL # allow for the export button to work
        self.export['command'] = self.Export
        self.view['state'] = DISABLED # disable the view button
        self.prepFields()
    
    def OpenDir(self):
    
        if (self.DefaultDirectory == self.root) or (Path(self.DefaultDirectory).is_dir() == False):
            self.DefaultDirectory = self.root

        directory = filedialog.askdirectory(initialdir = self.DefaultDirectory, title = "Choose folder from which to process")

        try:
            for i in sorted(os.listdir(directory)):
                if (not os.path.isdir(directory + SLASH + i)) and (getFileExt(i) == ".atf" or getFileExt(i) == ".axgr"):                  
                    self.DefaultDirectory = directory
                    self.InputFileName = (self.DefaultDirectory + '/' + i)

                    self.inputtext['text'] = "(Entire Directory)"
                    self.inputtext.unbind("<Button-1>")
                    self.inputtext["cursor"] = ""
                    
                    self.Processor = DataProcessor()
                    self.Processor.Extract(self.InputFileName)
                    
                    self.srctext['text'] = self.DefaultDirectory
                    
                    self.GUIPrint("") # clear console
                    
                    self.export['state'] = NORMAL # allow for the export button to work
                    self.export['command'] = self.ExportDir
                    self.view['state'] = DISABLED # disable the view button
                    self.prepFields()

                    return True
                    
            self.GUIPrint("No files in /.../" + directory[directory.rfind("/")+1:] + "/ to process.")        
            return False
                    
        except FileNotFoundError as e:
            return False
            
    def prepFields(self): 
        # Default field values
        self.BaselineStart = self.Processor.getTimeFromPercent(.3)
        self.BaselineEnd = self.Processor.getTimeFromPercent(.3333333)
        self.OnsetStart = self.Processor.getTimeFromPercent(.3333333)
        self.OnsetEnd = self.Processor.getTimeFromPercent(.4333333)
        self.DeviationMultiplier = 3  
        self.PlusInitialPeak = 5
        self.PlusMaxPeak = 25
        self.PlusMaxSlope = 5
        self.RegressionPoints = 20
        
        self.setFieldText(self.BaselineStartField, self.BaselineStart)
        self.setFieldText(self.BaselineEndField, self.BaselineEnd)
        self.setFieldText(self.OnsetStartField, self.OnsetStart)
        self.setFieldText(self.OnsetEndField, self.OnsetEnd)
        self.setFieldText(self.StdDevField, self.DeviationMultiplier)
        self.setFieldText(self.InitialPeakField, self.PlusInitialPeak)
        self.setFieldText(self.MaxPeakField, self.PlusMaxPeak)
        self.setFieldText(self.MaxSlopeField, self.PlusMaxSlope)
        self.setFieldText(self.RegressionField, self.RegressionPoints)
        
        self.BaselineStartField.bind("<Button-1>", lambda x: [changeState(self.BaselineStartField), self.BaselineStartField.bind('<Return>', self.BaselineStartEnter)])
        self.BaselineEndField.bind("<Button-1>", lambda x: [changeState(self.BaselineEndField), self.BaselineEndField.bind('<Return>', self.BaselineEndEnter)])
        self.OnsetStartField.bind("<Button-1>", lambda x: [changeState(self.OnsetStartField), self.OnsetStartField.bind('<Return>', self.OnsetStartEnter)])
        self.OnsetEndField.bind("<Button-1>", lambda x: [changeState(self.OnsetEndField), self.OnsetEndField.bind('<Return>', self.OnsetEndEnter)])
        self.StdDevField.bind("<Button-1>", lambda x: [changeState(self.StdDevField), self.StdDevField.bind('<Return>', self.StdDevEnter)])
        self.InitialPeakField.bind("<Button-1>", lambda x: [changeState(self.InitialPeakField), self.InitialPeakField.bind('<Return>', self.InitialPeakEnter)])
        self.MaxPeakField.bind("<Button-1>", lambda x: [changeState(self.MaxPeakField), self.MaxPeakField.bind('<Return>', self.MaxPeakEnter)])
        self.MaxSlopeField.bind("<Button-1>", lambda x: [changeState(self.MaxSlopeField), self.MaxSlopeField.bind('<Return>', self.MaxSlopeEnter)])
        self.RegressionField.bind("<Button-1>", lambda x: [changeState(self.RegressionField), self.RegressionField.bind('<Return>', self.RegressionEnter)])
         
    def setFieldText(self, TextField, Value):
        TextField['state'] = NORMAL
        TextField.delete(0, 'end')
        TextField.insert(0, Value)
        TextField['state'] = DISABLED

    def ValidateInputs(self):
        if (self.BaselineStart < self.BaselineEnd) and (self.OnsetStart < self.OnsetEnd) and (self.BaselineEnd <= self.OnsetStart):
            if (self.RegressionPoints <= (self.PlusMaxSlope * 10)):
                return True
        return False  

    def OutputFolderChoose(self):
        dir = filedialog.askdirectory(initialdir = self.OutputDirectory, title = "Choose folder to store reports in")
        if (dir != ""): # The user chose a folder
            self.OutputDirectory = dir 
            self.GUIPrint("Output folder changed: " + self.OutputDirectory )
            print("Output folder changed: " + self.OutputDirectory )
            self.export.bind('<Button-3>', self.OutputFolderChange) 
            return True;
        else: # The user selected cancel
            print("No output folder chosen.")
            self.GUIPrint("ERROR: Please choose a folder to store processing reports to complete the processing.")
            return False
        
    def OutputFolderCheck(self):
        if (self.OutputDirectory == str(self.root)) or (Path(self.OutputDirectory).is_dir() == False):
            self.OutputDirectory = str(self.root)
            return self.OutputFolderChoose()
        return True;
    
    def OutputFolderChange(self, event):
        MsgBox = messagebox.askquestion("Change output folder?", "Would you like to change the folder to which the reports are being saved?")
        if (MsgBox == 'no'):
            return False
        else:
            self.OutputFolderChoose()
                        
    def Export(self):
        if self.ValidateInputs():
            if not self.OutputFolderCheck():
                return None;
            self.Processor.Process(self.BaselineStart, self.BaselineEnd, self.OnsetStart, self.OnsetEnd, self.DeviationMultiplier, self.PlusInitialPeak, self.PlusMaxPeak, self.PlusMaxSlope, self.RegressionPoints)
            
            if GRAPH == True:
                self.showGraph(self.InputFileName, self.Processor.getAxographFile()) if (self.Processor.isGraphable()) else self.clearGraph()   
                    
            if (self.OutputFileType == ".txt"):
                self.OutputToTxt(); 
            elif (self.OutputFileType == ".xlsx"):
                # Create an excel file
                self.OutputExcelFile = self.InitXLSX(self.InputFileName[self.InputFileName.rfind('/')+1:] + " Report")
                if (self.OutputExcelFile == None):
                    return False
                # Create sheets in the excel file
                OnsetSheet = self.CreateXLSXSheet("Response Onset Latency")
                InitialPeakSheet = self.CreateXLSXSheet("Initial Peak Amplitude")
                MaxPeakSheet = self.CreateXLSXSheet("Max Peak Amplitude") 
                MaxPeakLSheet = self.CreateXLSXSheet("Max Peak Latency") 
                MaxSlopeSheet = self.CreateXLSXSheet("Initial Max Slope") 
                # Call a self.function() appending the contents of the current self.Processor to the end of the excel file                
                self.OutputToXLSX(OnsetSheet, self.Processor.getOnsetLatency())
                self.OutputToXLSX(InitialPeakSheet, self.Processor.getInitialPeak())
                self.OutputToXLSX(MaxPeakSheet, self.Processor.getMaxPeak())
                self.OutputToXLSX(MaxPeakLSheet, self.Processor.getMaxLPeak())
                self.OutputToXLSX(MaxSlopeSheet, self.Processor.getMaxSlope())
                # Close the excel file  
                self.OutputExcelFile.close() 
                print(self.OutputFileName + " created in source folder subdirectory.")
                self.GUIPrint(self.OutputFileName + " created in source folder subdirectory.")
            self.view['command'] = self.ViewFile
            self.view['state'] = NORMAL

        else:
            self.GUIPrint("ERROR: Slider values are not logical.")
        
    def ExportDir(self):
        if self.ValidateInputs():
            if not self.OutputFolderCheck():
                return None;
            message = "Process all .AXGR and .ATF files in " + self.DefaultDirectory + " with the variables inputted? This will overwrite any prexisting reports of those files in the output folder."
            MsgBox = messagebox.askquestion("Process all files?", message)
            if (MsgBox == 'no'):
                return False
            else:
                threading.Thread(target=self.ExportDirThread).start() 
        else:
            self.GUIPrint("ERROR: Slider values are not logical.")
    
    def ExportDirThread(self):
        if self.OutputFileType == ".xlsx":
            # Create an excel file
            self.OutputExcelFile = self.InitXLSX(self.DefaultDirectory[self.DefaultDirectory.rfind("/")+1:] + " Report")
            if (self.OutputExcelFile == None):  
                return False
            # Create sheets in the excel file    
            OnsetSheet = self.CreateXLSXSheet("Response Onset Latency")
            InitialPeakSheet = self.CreateXLSXSheet("Initial Peak Amplitude")
            MaxPeakSheet = self.CreateXLSXSheet("Max Peak Amplitude") 
            MaxPeakLSheet = self.CreateXLSXSheet("Max Peak Latency") 
            MaxSlopeSheet = self.CreateXLSXSheet("Initial Max Slope") 
            
        self.root['cursor'] = "watch"    
        column_counter = 0
        for possible_file in sorted(os.listdir(self.DefaultDirectory)):
            if (not os.path.isdir(self.DefaultDirectory + SLASH + possible_file)) and (getFileExt(possible_file) == ".atf" or getFileExt(possible_file) == ".axgr"): 
                self.InputFileName = (self.DefaultDirectory + '/' + possible_file)
                self.Processor = DataProcessor()
                self.Processor.Extract(self.InputFileName)
                self.Processor.Process(self.BaselineStart, self.BaselineEnd, self.OnsetStart, self.OnsetEnd, self.DeviationMultiplier, self.PlusInitialPeak, self.PlusMaxPeak, self.PlusMaxSlope, self.RegressionPoints)
                     
                if GRAPH == True:
                    self.showGraph(self.InputFileName, self.Processor.getAxographFile()) if (self.Processor.isGraphable()) else self.clearGraph()   
                    
                if (self.OutputFileType == ".txt"):
                    self.OutputToTxt();                                   
                    self.view['command'] = self.ViewDir
                    outputtitle = "source folder subdirectory."
                elif (self.OutputFileType == ".xlsx"):
                    column_counter += 1
                    print("Processing " + self.InputFileName[self.InputFileName.rfind('/')+1:self.InputFileName.find(".")])
                    self.GUIPrint("Processing " + self.InputFileName[self.InputFileName.rfind('/')+1:self.InputFileName.find(".")])
                    # Call a self.function() appending the contents of the current self.Processor to the end of the excel file   
                    self.OutputToXLSX(OnsetSheet, self.Processor.getOnsetLatency(), column_counter)
                    self.OutputToXLSX(InitialPeakSheet, self.Processor.getInitialPeak(), column_counter)
                    self.OutputToXLSX(MaxPeakSheet, self.Processor.getMaxPeak(), column_counter)
                    self.OutputToXLSX(MaxPeakLSheet, self.Processor.getMaxLPeak(), column_counter)
                    self.OutputToXLSX(MaxSlopeSheet, self.Processor.getMaxSlope(), column_counter)
                    
                    outputtitle = self.OutputFileName
                    self.view['command'] = self.ViewFile
                self.view['state'] = NORMAL
                
        if self.OutputFileType == ".xlsx":  
            # Close the excel file          
            self.OutputExcelFile.close()   
        self.GUIPrint("All files processed into " + outputtitle)  
        print("All files processed into " + outputtitle)  
        self.root['cursor'] = ""    
    
    def ViewDir(self):
        if os.path.isdir(self.OutputDirectory):
            openFile(self.OutputDirectory)
        else:
            self.GUIPrint("ERROR: " + self.OutputDirectory + " can't been found.")
        
    def ViewFile(self):
        if os.path.isfile(self.OutputDirectory + SLASH + self.OutputFileName):
            openFile(self.OutputDirectory + SLASH + self.OutputFileName)
        else:
            self.GUIPrint("ERROR: " + self.OutputFileName + " has been deleted.")

    def InitXLSX(self, name):
        try:                
            # Make output file name     
            self.OutputFileName = name + ".xlsx"
            oname = self.OutputDirectory + SLASH + self.OutputFileName
            
            # Open and initialize file
            counter = 1
            while True:
                if os.path.isfile(oname):
                    counter += 1
                    self.OutputFileName = name + " (" + str(counter) + ").xlsx"
                    oname = self.OutputDirectory + SLASH + self.OutputFileName
                else:
                    break
            
            return xlsxwriter.Workbook(oname)  
        except PermissionError as e:
            self.GUIPrint("ERROR: " + self.OutputFileName + " in use; can't be modified.")
            return None

    def CreateXLSXSheet(self, name):
        bold = self.OutputExcelFile.add_format({'bold': True})
        this_sheet = self.OutputExcelFile.add_worksheet(name)
        this_sheet.write(0, 0, "Channels", bold)
        for num in range(self.Processor.getNumberOfChannels()): # only gets # of channels for the first file
            this_sheet.write(num+1, 0, num+1, bold)
        
        return this_sheet
    
    def OutputToXLSX(self, this_sheet, dictionary, column_counter=1, units="ms"): 
        counter = 1
        bold = self.OutputExcelFile.add_format({'bold': True})
        round = self.OutputExcelFile.add_format({'num_format': '0.0000'})
        this_sheet.set_column(column_counter, column_counter, 15)
        this_sheet.write(0, column_counter, self.InputFileName[self.InputFileName.rfind('/')+1:self.InputFileName.find(".")], bold)
        for channelitem in dictionary:
            value = dictionary[channelitem]
            if value != "(?)" and value != 0:
                this_sheet.write(counter, column_counter, value, round) #round(value, 3)
            counter += 1
        
        self.GUIPrint("Processing " + self.InputFileName[self.InputFileName.rfind('/')+1:self.InputFileName.find(".")])
        
    def OutputToTxt(self):
        # Make output file name
        self.OutputFileName = self.InputFileName[self.InputFileName.rfind('/')+1:self.InputFileName.find(".")] + " Report.txt"  
        oname = self.OutputDirectory + SLASH + self.OutputFileName
   
        # Open and initialize file
        outputfile = open(oname,"w")
        outputfile.write(oname[oname.rfind("\\")+1:] + "\n" + datetime.datetime.now().strftime("%Y-%m-%d, Time %H:%M:%S") + "\n")
        outputfile.write(str(self.Processor.getNumberOfLines()) + " datapoints, " + str(self.Processor.getNumberOfChannels()) + " channels." + "\n\n")
      
        self.OutputToTxtWrite(outputfile, "Onset Latency", self.Processor.getOnsetLatency())
        self.OutputToTxtWrite(outputfile, ("Initial Peak Amplitude (+ " + str(self.PlusInitialPeak) + " ms)"), self.Processor.getInitialPeak())
        self.OutputToTxtWrite(outputfile, ("Max Peak Amplitude (+ " + str(self.PlusMaxPeak) + " ms)"), self.Processor.getMaxPeak())
        self.OutputToTxtWrite(outputfile, ("Max Peak Latency (+ " + str(self.PlusMaxPeak) + " ms)"), self.Processor.getMaxLPeak())
        self.OutputToTxtWrite(outputfile, ("Initial Max Slope (+ " + str(self.PlusMaxSlope) + " ms)"), self.Processor.getMaxSlope())
        
        outputfile.close() #print(oname[oname.rfind("\\")+1:] + " created.")
        
        print(self.OutputFileName + " created in output folder.")
        self.GUIPrint(self.OutputFileName + " created in output folder.")
        
    def OutputToTxtWrite(self, outputfile, title, OutputDict):
        outputfile.write(title+":\n")
        for channel in OutputDict:
            outputfile.write(str(channel) + ": " + str(OutputDict[channel]) + "\n")
        outputfile.write("\n")  
     
    def BaselineStartEnter(self, event):
        try:
            f = float(self.BaselineStartField.get())
            if self.Processor.inTimeRange(f):
                self.BaselineStartField['state'] = DISABLED
                self.BaselineStart = f
                print("New value: ", f)
                self.GUIPrint("")
            else:
                raise Exception
        except:
            #traceback.print_exc()
            self.GUIPrint("ERROR: " + "Baseline start value not within time range.")

    def BaselineEndEnter(self, event):
        try:
            f = float(self.BaselineEndField.get())
            if self.Processor.inTimeRange(f):
                self.BaselineEndField['state'] = DISABLED
                self.BaselineEnd = f
                print("New value: ", f)
                self.GUIPrint("")
            else:
                raise Exception
        except:
            #traceback.print_exc()
            self.GUIPrint("ERROR: " + "Baseline end value not within time range.")

    def OnsetStartEnter(self, event):
        try:
            f = float(self.OnsetStartField.get())
            if self.Processor.inTimeRange(f):
                self.OnsetStartField['state'] = DISABLED
                self.OnsetStart = f
                print("New value: ", f)
                self.GUIPrint("")
            else:
                raise Exception
        except:
            #traceback.print_exc()
            self.GUIPrint("ERROR: " + "Onset start value not within time range.")

    def OnsetEndEnter(self, event):
        try:
            f = float(self.OnsetEndField.get())
            if self.Processor.inTimeRange(f):
                self.OnsetEndField['state'] = DISABLED
                self.OnsetEnd = f
                print("New value: ", f)
                self.GUIPrint("")
            else:
                raise Exception
        except:
            #traceback.print_exc()
            self.GUIPrint("ERROR: " + "Onset start value not within time range.")

    def InitialPeakEnter(self, event):
        try:
            f = float(self.InitialPeakField.get())
            if self.Processor.inTimeRange(f):
                self.InitialPeakField['state'] = DISABLED
                self.PlusInitialPeak = f
                print("New value: ", f)
                self.GUIPrint("")
            else:
                raise Exception
        except:
            #traceback.print_exc()
            self.GUIPrint("ERROR: " + "Initial peak additive value not within time range.")

    def MaxPeakEnter(self, event):
        try:
            f = float(self.MaxPeakField.get())
            if self.Processor.inTimeRange(f):
                self.MaxPeakField['state'] = DISABLED
                self.PlusMaxPeak = f
                print("New value: ", f)
                self.GUIPrint("")
            else:
                raise Exception
        except:
            #traceback.print_exc()
            self.GUIPrint("ERROR: " + "Max peak additive value not within time range.") 

    def MaxSlopeEnter(self, event):
        try:
            f = float(self.MaxSlopeField.get())
            if self.Processor.inTimeRange(f):
                self.MaxSlopeField['state'] = DISABLED
                self.PlusMaxSlope = f
                print("New value: ", f)
                self.GUIPrint("")
            else:
                raise Exception
        except:
            #traceback.print_exc()
            self.GUIPrint("ERROR: " + "Max slope additive value not within time range.") 

    def StdDevEnter(self, event):
        try:
            f = int(self.StdDevField.get())
            if (f > 0):
                self.StdDevField['state'] = DISABLED
                self.DeviationMultiplier = f
                print("New value: ", f)
                self.GUIPrint("")
            else:
                raise Exception
        except:
            #traceback.print_exc()
            self.GUIPrint("ERROR: " + "Standard deviation not a valid number.")
            
    def RegressionEnter(self, event):
        try:
            f = int(self.RegressionField.get())
            if (f <= (int(self.MaxSlopeField.get()) * 10)):
                self.RegressionField['state'] = DISABLED
                self.RegressionPoints = f
                print("New value: ", f)
                self.GUIPrint("")
            else:
                raise Exception
        except:
            self.GUIPrint("ERROR: " + "Regression not a valid number (no greater than addend * 10).") #traceback.print_exc()
               
    def SelectOutputType(self, event):
        self.OutputFileType = self.ComboBox.get()

if __name__ == "__main__":       
    GUI = DataProcessorGUI()










