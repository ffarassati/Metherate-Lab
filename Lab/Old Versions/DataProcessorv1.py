from tkinter import filedialog
from tkinter import *
import statistics
import datetime

def ATFstrip(file_object):
    for x in range(5):
        file_object.readline()
    return file_object

root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select ATF file (Axograph -> Export -> Axon Text Format)",filetypes = (("ATF Files","*.atf"),("all files","*.*")))
inputfile = ATFstrip(open(root.filename, "r"))

NumberOfChannels = 14
NumberOfLines = 0
Channels = {x+1:[] for x in range(NumberOfChannels)}
Time = []

for line in inputfile.readlines():
    NumberOfLines += 1;
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



def peak(channel):
    maxvalue = 0.0
    time = 0.0
    base = int(NumberOfLines / 3)
    while base <= int(NumberOfLines / 2.307): 
        if abs(Channels[channel][base]) > abs(maxvalue):
            maxvalue = Channels[channel][base]
            time = base
        base += 1
    return (time, maxvalue)

def stddeviation(channel):
    base = int(NumberOfLines / 3.333)
    datapoints = []
    while base <= int(NumberOfLines / 3):
        datapoints.append(Channels[channel][base])
        base += 1
    return statistics.stdev(datapoints)

def onset(channel):
    time = peak(channel)[0]
    maxvalue = peak(channel)[1]
    onset = 3 * stddeviation(channel)
    if maxvalue < 0:
        onset = onset * -1
        while time > int(NumberOfLines / 3):
            if Channels[channel][time] >= onset:
                return (Time[time], onset) # does he want an estimated time or the nearest time in the data?
            time -= 1
    else:
        while time > int(NumberOfLines / 3):
            if Channels[channel][time] <= onset:
                return (Time[time], onset)
            time -= 1

def slopeonsetpeak(channel):
    p = peak(channel)[1]
    pt = Time[peak(channel)[0]]
    o = onset(channel)[1]
    ot = onset(channel)[0]

    return ((p - o) / (pt - ot))
    

Peak = {x+1:0.0 for x in range(NumberOfChannels)}
Deviations = {x+1:0.0 for x in range(NumberOfChannels)}
OnsetLatency = {x+1:0.0 for x in range(NumberOfChannels)}
Slope = {x+1:0.0 for x in range(NumberOfChannels)}

for x in range(NumberOfChannels):
    channel = x + 1 # 1 through 14
    Peak[channel] = peak(channel)[1]
    Deviations[channel] = stddeviation(channel)
    OnsetLatency[channel] = onset(channel)
    Slope[channel] = slopeonsetpeak(channel)


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

##print("\n" + "Peak Amplitude:")
##for x in Peak:
##    print(x, ":", Peak[x])
##    
##print("\n" + "Onset Latency (milliseconds, amplitude):")
##for x in OnsetLatency:
##    print(x, ":", OnsetLatency[x])
##
##print("\n" + "Onset-Peak Slope:")
##for x in Slope:
##    print(x, ":", Slope[x])



    










