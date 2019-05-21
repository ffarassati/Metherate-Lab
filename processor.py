import axographio
import statistics
import math

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
        for index in range(len(self.Time)):
            if (not ms > self.Time[index]):
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
        #maxvalue = total / 41   
        
        return (self.Time[time], maxvalue) # [0] is the latency, [1] is the amplitude

    def stddeviation(self, channel, searchStart, searchEnd):
        datapoints = []
        for index in (range(self.msToTimeIndex(searchStart), self.msToTimeIndex(searchEnd))):
            datapoints.append(self.Channels[channel][index])
        return statistics.stdev(datapoints)

    def onsetHelper(self, channel, possible_onsets, total, portion):
        onset = "(?)"
        
        #print("Checking for", portion, "/", total, ":")
        for index in possible_onsets:
            asc_counter = 0
            for plus in range(total):
                if self.Channels[channel][index + plus] >= self.Channels[channel][index + plus - 1]:
                    asc_counter += 1
            
            desc_counter = 0
            for plus in range(total):
                if self.Channels[channel][index + plus] <= self.Channels[channel][index + plus - 1]:
                    desc_counter += 1              
            
            if (asc_counter >= portion):
                #print("found a good ascending:", self.Time[index])
                onset = self.Time[index]   
                break    
            elif (desc_counter >= portion):
                #print("found a good descending:", self.Time[index])
                onset = self.Time[index]   
                break
            #else:
                #print(self.Time[index], "only got ", (asc_counter if asc_counter > desc_counter else desc_counter))
                    
        return onset
    
    def onset(self, channel, StandardDeviation):
        OnsetPoint = self.DeviationMultiplier * StandardDeviation
        
        possible_onsets = []

        #print("Checking channel", channel)
        for index in (range(self.msToTimeIndex(self.OnsetStart), self.msToTimeIndex(self.OnsetEnd))):
            if (self.Channels[channel][index] >= OnsetPoint and self.Channels[channel][index+1] <= OnsetPoint) or (self.Channels[channel][index] <= OnsetPoint and self.Channels[channel][index+1] >= OnsetPoint) or (self.Channels[channel][index] >= (-1*OnsetPoint) and self.Channels[channel][index+1] <= (-1*OnsetPoint)) or (self.Channels[channel][index] <= (-1*OnsetPoint) and self.Channels[channel][index+1] >= (-1*OnsetPoint)):
                #possible_onsets.insert(0,index)
                possible_onsets.append(index)
                #print(self.Time[index],":", OnsetPoint, "is between", self.Channels[channel][index], "and", self.Channels[channel][index+1])
        
        for number in range(3):
            onset = self.onsetHelper(channel, possible_onsets, 30, (25 - (4*number)))
            if onset != "(?)":
                break
                  
        #print(onset,"determined as the onset") 
        #print("CHANNEL", channel,"WINNER:", onset)   
        #print("\n" * 4)           
        return onset        

    def greatestslope(self, channel, searchStart, searchEnd, RegressionPoints):
        #print("Channel " + str(channel))
        #print(" - ", searchStart, ":", self.msToTimeIndex(searchStart))
        #print(" - ", searchEnd, ":", self.msToTimeIndex(searchEnd))
        diff = self.msToTimeIndex(searchEnd) - self.msToTimeIndex(searchStart) # number of datapoints between start and end values
        #print(" - ", diff)
        #print(" - ", (diff / RegressionPoints))
        current = self.msToTimeIndex(searchStart)
        increment = diff / RegressionPoints
        #counter = 0
        latency = current
        slope = 0
        while (current < self.msToTimeIndex(searchEnd)):
            #counter += 1
            new = current + increment
            #print("          ", counter, ":", self.Time[round(current)], "to", self.Time[round(new)])
            #print("          ", counter, ":", self.Channels[channel][round(current)], "to", self.Channels[channel][round(new)])
            s = ((self.Channels[channel][round(new)] - self.Channels[channel][round(current)]) / (self.Time[round(new)] - self.Time[round(current)]))
            if abs(s) > abs(slope):
                slope = s;
                latency = self.Time[round(current)]
                #print("          better slope!:", slope)  
            current = new
        #print("          max slope:", slope)

        return(latency, slope)

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
        self.MaxLPeak = self.emptyChannelsDict()
        self.InitialMaxSlope = self.emptyChannelsDict()
        
        for i in range(self.NumberOfChannels):
            channel = i + 1 # 1 through 14
            StandardDeviation = self.stddeviation(channel, self.BaselineStart, self.BaselineEnd)
            self.OnsetLatency[channel] = self.onset(channel, StandardDeviation)
            if (self.OnsetLatency[channel] != "(?)"):
                ThisOnset = self.OnsetLatency[channel]
                self.InitialPeak[channel] = self.peak(channel, ThisOnset, ThisOnset + self.PlusInitialPeak)[1]
                MaxPeakStuff = self.peak(channel, ThisOnset, ThisOnset + self.PlusMaxPeak)
                self.MaxPeak[channel] = MaxPeakStuff[1]
                self.MaxLPeak[channel] = MaxPeakStuff[0]
                self.InitialMaxSlope[channel] = self.greatestslope(channel, ThisOnset, ThisOnset + self.PlusMaxSlope, self.RegressionPoints)[1]
              
    def getOnsetLatency(self):
        return self.OnsetLatency
        
    def getInitialPeak(self):
        return self.InitialPeak

    def getMaxPeak(self):
        return self.MaxPeak   

    def getMaxLPeak(self):
        return self.MaxLPeak
    
    def getMaxSlope(self):
        return self.InitialMaxSlope    

    def getInitialMaxSlope(self):
        return self.InitialMaxSlope  
        
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
        
    def getNumberOfChannels(self):
        return self.NumberOfChannels
     
    def getNumberOfLines(self):
        return self.NumberOfLines     


if __name__ == "__main__":
    pass








