import axographio
import statistics
import math

# User-Inputed (stay between changing files)
Slider_Left = 300/90
Slider_Mid = 300/100
Slider_Right = 300/130
DeviationMultiplier = 3

# Static functions
def getFileExt(path):
    # Returns the file extension (i.e. '.atf') from any file path string
    return(path[path.rfind('.'):])    
    
def skipTextLines(inputfile, number):
    for x in range(number): # skip lines in an ATF file
        inputfile.readline()     

class DataProcessor:
    def __init__(self):
        self.NumberOfChannels = 0
        self.NumberOfLines = 0
        self.Channels = {}
        self.Time = []

    def extractATF(self, file_name):
        inputfile = open(file_name, "r")

        skipTextLines(inputfile, 1)

        channelvalue = inputfile.readline() # ATF files write-in the number of columns
        self.NumberOfChannels = (int(channelvalue[channelvalue.rfind("\t") + 1:]) - 1)
        self.Channels = {x+1:[] for x in range(self.NumberOfChannels)} #literally 1-14

        skipTextLines(inputfile, 3)
        
        for line in inputfile.readlines(): # For each entire line of numerical floats
            for channel in range(self.NumberOfChannels + 1): # For each channel in the line
                if (channel == 0): # time channel
                    splitpoint = line.find("\t")
                    self.Time.append(float(line[0:splitpoint].strip())) # Time is a list of all time values
                    line = line[splitpoint+1:]
                else:
                    if (line.find("\t") != -1):
                        splitpoint = line.find("\t")
                        self.Channels[channel].append(float(line[0:splitpoint].strip())) # Channels is a dictionary of lists
                        line = line[splitpoint+1:]
                    elif (line.find("\t") == -1): # The last channel in the row
                        self.Channels[channel].append(float(line.strip()))
        self.NumberOfLines = len(self.Time)

    def extractAXGR(self, file_name):
        inputfile = axographio.read(file_name)
        for row in inputfile.data[0]: # Time column
            self.Time.append(float(row))       
        self.NumberOfChannels = len(inputfile.data[1:])
        self.Channels = {x+1:[] for x in range(self.NumberOfChannels)} #literally 1-14
        for x in range(14): # channel columns [1:14]
            for datavalue in inputfile.data[x+1]:  
                self.Channels[x+1].append(float(datavalue))
        self.NumberOfLines = len(self.Time)
        self.AxographFile = inputfile

    def msToTimeIndex(self, ms):
        #print("Looking for", ms)
        #print(self.Time)
        for index in range(len(self.Time)):
            #print(self.Time[index], (ms > self.Time[index]))
            if (not ms > self.Time[index]):
                #print(str(self.Time[index-1]) + "is the closest value")
                return (index - 1)

    def peak(self, channel, searchStart, searchEnd):
        maxvalue = 0.0
        time = 0
        
        for index in (range(self.msToTimeIndex(searchStart), self.msToTimeIndex(searchEnd))):
            if abs(self.Channels[channel][index]) > abs(maxvalue):
                maxvalue = self.Channels[channel][index]
                time = index
                
        # Average the peak to account for noise
        total = 0
        try:
            for index in range(-20, 21):
                total += self.Channels[channel][time + index]
        except Exception as e:
            pass # in case the loop goes past the end of the time window
        maxvalue = total / 41   
        
        return (self.Time[time], maxvalue)

    def stddeviation(self, channel, searchStart, searchEnd):
        datapoints = []
        for index in (range(self.msToTimeIndex(searchStart), self.msToTimeIndex(searchEnd))):
            datapoints.append(self.Channels[channel][index])
        return statistics.stdev(datapoints)

    def onset(self, channel, StandardDeviation):
        #self.OnsetStart, self.OnsetEnd, self.DeviationMultiplier)
        #time = self.peak(channel)[0]
        #maxvalue = self.peak(channel)[1]
        #print(stddeviation(channel)) if channel == 9 else None
        
        # for 10 milliseconds, 80% of the datapoints are higher/lower than 3/5 of the datapoints previous to it
        OnsetPoint = self.DeviationMultiplier * StandardDeviation
        #print(channel, "Onset point:", OnsetPoint)
        
        last_onset = "(?)"
        for index in (range(self.msToTimeIndex(self.OnsetStart), self.msToTimeIndex(self.OnsetEnd))):
            if (abs(self.Channels[channel][index]) >= abs(OnsetPoint) and abs(self.Channels[channel][index+1]) <= abs(OnsetPoint)) or (abs(self.Channels[channel][index]) <= abs(OnsetPoint) and abs(self.Channels[channel][index+1]) >= abs(OnsetPoint)):
                last_onset = self.Time[index]
                #print("Possible onset between (", self.Time[index], ")", self.Channels[channel][index], "and", self.Channels[channel][index+1], "(", self.Time[index], ")")

        
            
        # if maxvalue < 0:
            # onset = onset * -1
            # while time > int(self.NumberOfLines / Slider_Mid):
                # if self.Channels[channel][time] >= onset:
                    # return (self.Time[time], onset) # does he want an estimated time or the nearest time in the data?
                # time -= 1
        # else:
            # while time > int(self.NumberOfLines / Slider_Mid):
                # if self.Channels[channel][time] <= onset:
                    # return (self.Time[time], onset)
                # time -= 1
        return last_onset        

    def slopeonsetpeak(self, channel):
        p = self.peak(channel)[1]
        pt = self.Time[self.peak(channel)[0]]
        o = self.onset(channel)[1]
        ot = self.onset(channel)[0]
        
        try:
            slope = ((p - o) / (pt - ot))
        except:
            slope = "(?)" # An error is caused when the slope is undefined (peak and onset are on the same point...?)
        finally:
            return slope

    def emptyChannelsDict(self):
        return {x+1:0.0 for x in range(self.NumberOfChannels)}

    def Process(self, BaselineStart, BaselineEnd, OnsetStart, OnsetEnd, DeviationMultiplier, PlusInitialPeak, PlusMaxPeak, PlusMaxSlope, RegressionPoints):  
        self.BaselineStart = BaselineStart
        self.BaselineEnd = BaselineEnd
        self.OnsetStart = OnsetStart
        self.OnsetEnd = OnsetEnd
        self.DeviationMultiplier = DeviationMultiplier
        self.PlusInitialPeak = PlusInitialPeak
        self.PlusMaxPeak = PlusMaxPeak
        self.PlusMaxSlope = PlusMaxSlope
        self.RegressionPoints = RegressionPoints
        
        
        self.OnsetLatency = self.emptyChannelsDict()
        self.InitialPeak = self.emptyChannelsDict()
        self.MaxPeak = self.emptyChannelsDict()
        self.InitialMaxSlope = self.emptyChannelsDict()
        
        for i in range(self.NumberOfChannels):
            channel = i + 1 # 1 through 14
            StandardDeviation = self.stddeviation(channel, self.BaselineStart, self.BaselineEnd)
            self.OnsetLatency[channel] = self.onset(channel, StandardDeviation)
            if (self.OnsetLatency[channel] != "(?)"):
                ThisOnset = self.OnsetLatency[channel]
                #self.InitialMaxSlope[channel] = self.slopeonsetpeak(channel)
                self.InitialPeak[channel] = self.peak(channel, ThisOnset, ThisOnset + self.PlusInitialPeak)
                self.MaxPeak[channel] = self.peak(channel, ThisOnset, ThisOnset + self.PlusMaxPeak)
                 
    def Extract(self, filename):
        if (getFileExt(filename) == ".atf"):
            self.extractATF(filename)
        elif (getFileExt(filename) == ".axgr"):
            self.extractAXGR(filename) 
        
    def getAxographFile(self):
        return self.AxographFile;

    def isGraphable(self):
        if hasattr(self, 'AxographFile'):
            return True
        return False   

    def inTimeRange(self, f):
        if f < float(self.Time[-1])-1 and f > float(self.Time[0]):  
            return True
        return False    
        
    def getTimeFromPercent(self, DecimalValue):
        #print(DecimalValue, "x", self.Time[-1], "=", int(math.ceil(self.Time[-1]*DecimalValue)))
        return int(math.ceil(self.Time[-1]*DecimalValue))
    
    def getOnsetLatency(self):
        return self.OnsetLatency
        
    def getInitialPeak(self):
        return self.InitialPeak

    def getMaxPeak(self):
        return self.MaxPeak        

    def getInitialMaxSlope(self):
        return self.InitialMaxSlope  

    def getNumberOfChannels(self):
        return self.NumberOfChannels
     
    def getNumberOfLines(self):
        return self.NumberOfLines     


if __name__ == "__main__":
    pass








