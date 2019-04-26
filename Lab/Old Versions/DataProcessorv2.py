from tkinter import filedialog
from tkinter import *
import statistics
import datetime
import axographio
import matplotlib.pyplot as plt

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

def extractAXGR(file_name):
    inputfile = axographio.read(file_name)
    for row in inputfile.data[0]: # Time column
        Time.append(float(row))
    setNumberOfChannels(len(inputfile.data[1:]))
    for x in range(14): # channel columns [1:14]
        for datavalue in inputfile.data[x+1]:  
            Channels[x+1].append(float(datavalue))
    setNumberOfLines(len(Time))
    showGraph(file_name, inputfile)

def setNumberOfLines(numberoftimes):
    global NumberOfLines
    NumberOfLines = numberoftimes

def setNumberOfChannels(numberofchannels):
    global NumberOfChannels
    NumberOfChannels = numberofchannels
    global Channels
    Channels = {x+1:[] for x in range(NumberOfChannels)} #literally 1-14

def showGraph(file_name, inputfile):
    # General code for a matplotlib of the whole file (matplotlib)
    plt.rcParams['toolbar'] = 'None'
    plt.figure(num=file_name)
    x = inputfile.data[0]
    for i in range(14):
        plt.plot(x, inputfile.data[i+1])
    plt.xlabel(inputfile.names[0])
    plt.ylabel(inputfile.names[1]);
    plt.suptitle(file_name)
    plt.show()

def peak(channel):
    maxvalue = 0.0
    time = 0.0
    base = int(NumberOfLines / Slider_Mid)
    while base <= int(NumberOfLines / Slider_Right): 
        if abs(Channels[channel][base]) > abs(maxvalue):
            maxvalue = Channels[channel][base]
            time = base
        base += 1
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
    return ((p - o) / (pt - ot))

def Process():
    for x in range(NumberOfChannels):
        channel = x + 1 # 1 through 14
        Peak[channel] = peak(channel)[1]
        Deviations[channel] = stddeviation(channel)
        OnsetLatency[channel] = onset(channel)
        Slope[channel] = slopeonsetpeak(channel)

def OutputToText():      
    oname = (root.filename[:root.filename.find("_")])
    oname = oname[oname.rfind("/") + 1:] + " Report"
    outputfile = open(oname + ".txt","w")
    outputfile.write(oname + "\n" + datetime.datetime.now().strftime("%Y-%m-%d, Time %H:%M:%S") + "\n\n")
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
    print("Done! \"" + oname + "\" created in the processor's folder location.")
    print(NumberOfLines, "datapoints,", NumberOfChannels, "channels.")

# Main() #######################################


print("Starting program.")

# GUI Handling
debug = False
root = Tk()
if debug == False:
    root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Open for processing",filetypes = (("AXGR Files","*.axgr"), ("ATF Files","*.atf"),("All Files","*.*")))
    root.destroy()
elif debug == True:
    root.filename = "012519 062_csd.axgr"
    root.destroy()

# User-Inputed
Slider_Left = 3.333
Slider_Mid = 3.0
Slider_Right = 2.307
DeviationMultiplier = 3

# Derived by the program
NumberOfChannels = 0
NumberOfLines = 0
Channels = {}
Time = []

# Output value dictionaries (accesed by OutputToText())
Peak = {x+1:0.0 for x in range(NumberOfChannels)}
Deviations = {x+1:0.0 for x in range(NumberOfChannels)}
OnsetLatency = {x+1:0.0 for x in range(NumberOfChannels)}
Slope = {x+1:0.0 for x in range(NumberOfChannels)}

if (root.filename[root.filename.rfind('.'):] == ".atf"):
    extractATF(root.filename)
elif (root.filename[root.filename.rfind('.'):] == ".axgr"):
    extractAXGR(root.filename)
else:
    raise Exception("Unsupported file type")
Process()
OutputToText()


