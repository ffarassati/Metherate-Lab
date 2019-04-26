import statistics
import datetime
import os
from pathlib import Path
from tkinter import *
from tkinter import filedialog
import tkinter.ttk as ttk

import axographio
#import matplotlib
##import matplotlib.pyplot as plt
##from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
##from matplotlib.backend_bases import key_press_handler
##from matplotlib.figure import Figure
##matplotlib.use("TkAgg")



# import numpy

def extractATF(file_name):
    inputfile = open(file_name, "r")
    inputfile.readline()
    channelvalue = inputfile.readline() # ATF files write-in the number of columns
    setNumberOfChannels(int(channelvalue[channelvalue.rfind("\t") + 1:]) - 1)
    for x in range(3):
        inputfile.readline()
    for line in inputfile.readlines():
        for y in range(NumberOfChannels + 1):
            if (y == 0):
                splitpoint = line.find("\t")
                Time.append(float(line[0:splitpoint].strip()))
                line = line[splitpoint+1:]
            else:
                if (line.find("\t") != -1):
                    splitpoint = line.find("\t")
                    Channels[y].append(float(line[0:splitpoint].strip()))
                    line = line[splitpoint+1:]
                elif (line.find("\t") == -1):
                    Channels[y].append(float(line.strip()))
    setNumberOfLines(len(Time))
    #clearGraph()

def extractAXGR(file_name):
    inputfile = axographio.read(file_name)
    for row in inputfile.data[0]: # Time column
        Time.append(float(row))
    setNumberOfChannels(len(inputfile.data[1:]))
    for x in range(14): # channel columns [1:14]
        for datavalue in inputfile.data[x+1]:  
            Channels[x+1].append(float(datavalue))
    setNumberOfLines(len(Time))
    #showGraph(file_name, inputfile)

def setNumberOfLines(numberoftimes):
    global NumberOfLines
    NumberOfLines = numberoftimes

def setNumberOfChannels(numberofchannels):
    global NumberOfChannels
    NumberOfChannels = numberofchannels
    global Channels
    Channels = {x+1:[] for x in range(NumberOfChannels)} #literally 1-14

def showGraph(file_name, inputfile):
    global Canvas

    Canvas.get_tk_widget().pack_forget()
    
    fig = Figure(figsize=(5, 4), dpi=100)
    plt = fig.add_subplot(111)
    x = inputfile.data[0]
    for i in range(14):
        plt.plot(x, inputfile.data[i+1])

    Canvas = FigureCanvasTkAgg(fig, master=graph)
    Canvas.draw()
    Canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    Toolbar = NavigationToolbar2Tk(Canvas, graph)

def clearGraph():
    global Canvas
    if (Canvas != "None"):
        Canvas.destroy()
        
    fig = Figure(figsize=(2, 4), dpi=100)
    Canvas = FigureCanvasTkAgg(fig, master=graph)
    Canvas.draw()
    Canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

def peak(channel):
    maxvalue = 0.0
    time = 0.0
    base = int(NumberOfLines / Slider_Mid)
    while base <= int(NumberOfLines / Slider_Right): 
        if abs(Channels[channel][base]) > abs(maxvalue):
            maxvalue = Channels[channel][base]
            time = base
        base += 1
    #print(time, maxvalue) if channel == 9 else None
    return (time, maxvalue)

def stddeviation(channel):
    base = int(NumberOfLines / Slider_Left)
    datapoints = []
    while base <= int(NumberOfLines / Slider_Mid):
        datapoints.append(Channels[channel][base])
        base += 1
    return statistics.stdev(datapoints)

def onset(channel):
    time = peak(channel)[0]
    maxvalue = peak(channel)[1]
    #print(stddeviation(channel)) if channel == 9 else None
    onset = DeviationMultiplier * stddeviation(channel)
    if maxvalue < 0:
        onset = onset * -1
        while time > int(NumberOfLines / Slider_Mid):
            if Channels[channel][time] >= onset:
                return (Time[time], onset) # does he want an estimated time or the nearest time in the data?
            time -= 1
    else:
        while time > int(NumberOfLines / Slider_Mid):
            if Channels[channel][time] <= onset:
                return (Time[time], onset)
            time -= 1

def slopeonsetpeak(channel):
    p = peak(channel)[1]
    pt = Time[peak(channel)[0]]
    o = onset(channel)[1]
    ot = onset(channel)[0]
    
    try:
        slope = ((p - o) / (pt - ot))
    except:
        slope = "(?)" # An error is caused when the slope is undefined (peak and onset are on the same point...?)
    finally:
        return slope

def Process(Peak, Deviations, OnsetLatency, Slope):
    for x in range(NumberOfChannels):
        channel = x + 1 # 1 through 14
        Peak[channel] = (Time[peak(channel)[0]], peak(channel)[1])
        Deviations[channel] = stddeviation(channel)
        OnsetLatency[channel] = onset(channel)
        Slope[channel] = slopeonsetpeak(channel)

def OutputToText(oname, Peak, Deviations, OnsetLatency, Slope):
    outputfile = open(oname,"w")
    outputfile.write(oname[oname.rfind("\\")+1:] + "\n" + datetime.datetime.now().strftime("%Y-%m-%d, Time %H:%M:%S") + "\n")
    outputfile.write(str(NumberOfLines) + " datapoints, " + str(NumberOfChannels) + " channels." + "\n\n")
    outputfile.write("Peak Amplitude:\n")
    for x in Peak:
        outputfile.write(str(x) + ": " + str(Peak[x]) + "\n")
    outputfile.write("\n")
    outputfile.write("Onset Latency (milliseconds, amplitude):\n")
    for x in OnsetLatency:
        outputfile.write(str(x) + ": " + str(OnsetLatency[x]) + "\n")
    outputfile.write("\n")
    outputfile.write("Onset-Peak Slope:\n")
    for x in Slope:
        outputfile.write(str(x) + ": " + str(Slope[x]) + "\n")
    outputfile.write("\n")
    outputfile.close()
    #print(oname[oname.rfind("\\")+1:] + " created.")
    

def Print(string):
    consoletext['text'] = string

def resetAllDerivedVariables():
    global NumberOfChannels
    global NumberOfLines
    global Channels
    global Time
    global Peak
    global Deviations
    global OnsetLatency
    global Slope
    NumberOfChannels = 0
    NumberOfLines = 0
    Channels = {}
    Time = []
    Peak = {x+1:0.0 for x in range(NumberOfChannels)}
    Deviations = {x+1:0.0 for x in range(NumberOfChannels)}
    OnsetLatency = {x+1:0.0 for x in range(NumberOfChannels)}
    Slope = {x+1:0.0 for x in range(NumberOfChannels)}



# Main() #######################################

# User-Inputed (stay between changing files)
Slider_Left = 300/90
Slider_Mid = 300/100
Slider_Right = 300/130
DeviationMultiplier = 3

# Derived by the program
NumberOfChannels = 0
NumberOfLines = 0
Channels = {}
Time = []
Peak = {x+1:0.0 for x in range(NumberOfChannels)}
Deviations = {x+1:0.0 for x in range(NumberOfChannels)}
OnsetLatency = {x+1:0.0 for x in range(NumberOfChannels)}
Slope = {x+1:0.0 for x in range(NumberOfChannels)}
# to add a calc, put it here, to resetAllDerivedVariables, and to process


def OpenAndPlot():
    global DefaultDirectory

    if (DefaultDirectory == root) or not (Path(DefaultDirectory).is_dir()):
        DefaultDirectory = root
        
    root.filename = filedialog.askopenfilename(initialdir = DefaultDirectory,title = "Open", filetypes = (("AXGR Files","*.axgr"), ("ATF Files","*.atf")))

    if (root.filename[root.filename.rfind('.'):] != ".axgr" or root.filename[root.filename.rfind('.'):] == ".atf"):
        return False # If they pressed Cancel
   
    global InputFileName
    InputFileName = root.filename

    DefaultDirectory = root.filename[:root.filename.rfind("/")]

    resetAllDerivedVariables()

    if (root.filename[root.filename.rfind('.'):] == ".atf"):
        extractATF(root.filename)
    elif (root.filename[root.filename.rfind('.'):] == ".axgr"):
        extractAXGR(root.filename)

    #Process(Peak, Deviations, OnsetLatency, Slope)
    
    inputtext['text'] = InputFileName[InputFileName.rfind('/')+1:]
    Print("")
    export['state'] = NORMAL
    view['state'] = DISABLED

    FirstSliderText.bind("<Button-1>", lambda x: [ChangeState(FirstSliderText), FirstSliderText.bind('<Return>', FirstSliderEnter)])
    SecondSliderText.bind("<Button-1>", lambda x: [ChangeState(SecondSliderText), SecondSliderText.bind('<Return>', SecondSliderEnter)])
    ThirdSliderText.bind("<Button-1>", lambda x: [ChangeState(ThirdSliderText), ThirdSliderText.bind('<Return>', ThirdSliderEnter)])
    FourthSliderText.bind("<Button-1>", lambda x: [ChangeState(FourthSliderText), FourthSliderText.bind('<Return>', FourthSliderEnter)])
    
##def Export():
##    if (Slider_Left > Slider_Mid) and (Slider_Mid > Slider_Right):
##        Process(Peak, Deviations, OnsetLatency, Slope)
##        global OutputFileName
##        OutputFileName = InputFileName[InputFileName.rfind("/")+1:InputFileName.find(".")] + " Report" + ".txt"
##
##        global Directory
##        Directory = os.path.dirname(os.path.realpath(__file__)) + "\\" + os.path.basename(__file__) + " Outputs"
##        if not os.path.exists(Directory):
##            os.makedirs(Directory)
##            
##        OutputToText(Directory + "\\" + OutputFileName, Peak, Deviations, OnsetLatency, Slope)
##        Print(OutputFileName + " created in root directory.")
##        view['state'] = NORMAL
##    else:
##        Print("Slider values are not logical.")
##
##def View():
##    if os.path.isfile(Directory + "\\" + OutputFileName):
##        os.startfile(Directory + "\\" + OutputFileName)
##    else:
##        Print(OutputFileName + " has been deleted.")

def Export():
    if (Slider_Left > Slider_Mid) and (Slider_Mid > Slider_Right):
        Process(Peak, Deviations, OnsetLatency, Slope)
        global OutputFileName
        OutputFileName = InputFileName[InputFileName.rfind("/")+1:InputFileName.find(".")] + " Report" + ".txt"

        global Directory
        Directory = os.path.dirname(os.path.realpath(__file__)) + "/" + os.path.basename(__file__) + " Outputs"
        if not os.path.exists(Directory):
            os.makedirs(Directory)
            
        OutputToText(Directory + "/" + OutputFileName, Peak, Deviations, OnsetLatency, Slope)
        Print(OutputFileName + " created in root directory.")
        view['state'] = NORMAL
    else:
        Print("Slider values are not logical.")

def View():
    if os.path.isfile(Directory + "/" + OutputFileName):
        os.startfile(Directory + "/" + OutputFileName)
    else:
        Print(OutputFileName + " has been deleted.")


        
# GUI - TK() 
root = Tk()
root.wm_title(os.path.basename(__file__))
root.geometry("500x550")
root.resizable(False, False)

OutputFileName = ""
InputFileName = ""
Canvas = "None"
Directory = ""
DefaultDirectory = root

# GUI - Frames
taskbar = Frame(root)
taskbar.pack(fill = X)
taskbar.columnconfigure(0, weight=1)
taskbar.columnconfigure(1, weight=9)
taskbar.columnconfigure(2, weight=1)
taskbar.columnconfigure(3, weight=1)
taskbar.columnconfigure(4, weight=1)
taskbar.columnconfigure(5, weight=1)

settings = Frame(root)
settings.pack(fill = X)
settings.columnconfigure(0, weight=1)
settings.columnconfigure(1, weight=1)
settings.columnconfigure(2, weight=1)
settings.columnconfigure(3, weight=1)
settings.columnconfigure(4, weight=1)
settings.columnconfigure(5, weight=1)
settings.columnconfigure(6, weight=1)
settings.columnconfigure(7, weight=1)
settings.columnconfigure(8, weight=1)

output = Frame(root)
output.pack(fill = X)
output.columnconfigure(0, weight=1)

#graph = Frame(root)
#graph.pack(fill = X, side = BOTTOM)

# GUI - Button
openfile = Button(master=taskbar, text="Open", command=OpenAndPlot, width = 5)
openfile.grid(row=0, column=0, sticky=W+E, padx=5, pady=5)
openfile['state'] = NORMAL

export = Button(master=taskbar, text="Process", command=Export, width = 5)
export.grid(row=0, column=4, sticky=W+E, padx=3, pady=5)
export['state'] = DISABLED

view = Button(master=taskbar, text="View", command=View, width = 5)
view.grid(row=0, column=5, sticky=W+E, padx=3, pady=5)
view['state'] = DISABLED

# GUI - Labels
inputtext = Label(taskbar, text="")
inputtext.grid(row=0, column=1, sticky=W, pady=5)

exporttext = Label(taskbar, text="Export as:")
exporttext.grid(row=0, column=2, sticky=E, pady=5)

FirstSlider = Label(settings, text="First slider:", pady = 3)
FirstSlider.grid(row=0, column=0, sticky=E)

SecondSlider = Label(settings, text="Second slider:", pady = 3)
SecondSlider.grid(row=0, column=2, sticky=E)

ThirdSlider = Label(settings, text="Third slider:",  pady = 3)
ThirdSlider.grid(row=0, column=4, sticky=E)

FourthSlider = Label(settings, text="Multiplier:", pady = 3)
FourthSlider.grid(row=0, column=6, sticky=E)

Gap = Label(settings, text="  ", pady = 3)
Gap.grid(row=0, column=8, sticky=E)


consoletext = Label(output, text="", padx = 3, pady = 3, fg="gray", font=("TkDefaultFont", 8))
consoletext.grid(row=0, column=0, sticky=W+E)

#GUI Text Entry

def ChangeState(TextEntry):
    TextEntry['state'] = NORMAL

def FirstSliderEnter(event):
    global Slider_Left
    try:
        f = float(FirstSliderText.get())
        if f < float(Time[-1])-1 and f > float(Time[0]):
            FirstSliderText['state'] = DISABLED
            Slider_Left = Time[-1] / f
            Print("")
        else:
            raise Exception
    except:
        Print("Value of " + FirstSlider['text'][:-1].lower() + " not within time range")

FirstSliderText = Entry(settings, width = 6)
FirstSliderText.insert(END, 90)
FirstSliderText['state'] = DISABLED
FirstSliderText.grid(row=0, column=1, sticky=W)

def SecondSliderEnter(event):
    global Slider_Mid
    try:
        f = float(SecondSliderText.get())
        if f < float(Time[-1])-1 and f > float(Time[0]):
            SecondSliderText['state'] = DISABLED
            Slider_Mid = Time[-1] / f
            Print("")
        else:
            raise Exception
    except:
        Print("Value of " + SecondSlider['text'][:-1].lower() + " not within time range")
SecondSliderText = Entry(settings, width = 6)
SecondSliderText.insert(END, 100)
SecondSliderText['state'] = DISABLED
SecondSliderText.grid(row=0, column=3, sticky=W)

def ThirdSliderEnter(event):
    global Slider_Right
    try:
        f = float(ThirdSliderText.get())
        if f < float(Time[-1])-1 and f > float(Time[0]):
            ThirdSliderText['state'] = DISABLED
            Slider_Right = Time[-1] / f
            Print("")
        else:
            raise Exception
    except:
        Print("Value of " + ThirdSlider['text'][:-1].lower() + " not within time range")
ThirdSliderText = Entry(settings, width = 6)
ThirdSliderText.insert(END, 130)
ThirdSliderText['state'] = DISABLED
ThirdSliderText.grid(row=0, column=5, sticky=W)


def FourthSliderEnter(event):
    global Deviation_Multiplier
    try:
        f = float(FourthSliderText.get())
        FourthSliderText['state'] = DISABLED
        DeviationMultiplier = f
        Print("")
    except:
        Print("Value of " + FourthSlider['text'][:-1].lower() + " not a valid number")
        
FourthSliderText = Entry(settings, width = 6)
FourthSliderText.insert(END, 3)
FourthSliderText['state'] = DISABLED
FourthSliderText.grid(row=0, column=7, sticky=W)


# GUI - Combo Box
def on_select(event):
    print(cb.get())
    
cb = ttk.Combobox(taskbar, values=(".txt", ".xlsx"), width = 2) # .exe support coming soon
cb.set(".txt")
cb.grid(row=0, column=3, sticky=W+E, pady=5)
cb.bind('<<ComboboxSelected>>', on_select)

# GUI - Initial State
#clearGraph()

# GUI - Start
mainloop()




