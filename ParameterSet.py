import AnalysableAudioFile

# TODO
            # create special parameters which check time similarity by using euclidean distance over dynamics. (creates heavy load!)
            # option 1: save time similarity point inside a point (i.e. [param, param, [time1, time2, time3], param]
            #   then let euclidean distance check subarrays first for euclidean distance.

class ParameterSet:
    isLoadedFromFile = False
    isGenerated = False

    af = None
    STATEID = ""
    # string list
    PARAMETERS_STRING = "sub, punch, lowmid, mid, highmid, highs, duration, median, average, spatialness, devOverTimeShort, devOverTime, devOverTime2, devOverTimeLong, dynamicsLong, dynamicsShort, loudestFreq"
    PARAMETERS = PARAMETERS_STRING.split(", ")
    IDENTIFIER = PARAMETERS_STRING + STATEID
    # parameters as single string + identifier
    values = None # float list

    def __init__(self, analysableaudiofile, values=None):
        self.af = analysableaudiofile

        if values is not None:
            self.values = values
            self.isLoadedFromFile = True

    def generateState(self):
        self.af.load()

        if self.values is None:
            # TESTING
            # print("All:", af.getMagnitudeForFrequencyRange(0, 50000))
            # sub4 = af.getMagnitudeForFrequencyRange(26, 73)
            # sub3 = af.getMagnitudeForFrequencyRange(73, 156)
            # sub2 = af.getMagnitudeForFrequencyRange(156, 312)
            # sub = af.getMagnitudeForFrequencyRange(312, 625)
            # punch = af.getMagnitudeForFrequencyRange(625, 1250)
            # lowmid = af.getMagnitudeForFrequencyRange(1250, 2500)
            # mid = af.getMagnitudeForFrequencyRange(2500, 5000)
            # highmid = af.getMagnitudeForFrequencyRange(5000, 10000)
            # highs = af.getMagnitudeForFrequencyRange(10000, 20000)
            # lows = af.getMagnitudeForFrequencyRange(0, 10000)
            # afState.append([sub4, sub3, sub2, sub, punch, lowmid, mid, highmid, highs, lows])

            sub = self.af.getMagnitudeForFrequencyRange(20, 100)
            punch = self.af.getMagnitudeForFrequencyRange(100, 300)
            lowmid = self.af.getMagnitudeForFrequencyRange(300, 500)
            mid = self.af.getMagnitudeForFrequencyRange(500, 1000)
            highmid = self.af.getMagnitudeForFrequencyRange(1000, 2000)
            highs = self.af.getMagnitudeForFrequencyRange(2000, 20000)
            duration = self.af.getSigmoidDuration()
            median = self.af.getMedianAmp()
            average = self.af.getAverageAmp()  # checked
            spatialness = self.af.getSpatialness()  # checked
            devOverTimeShort = self.af.getTransientAmount(0.01)
            devOverTime2 = self.af.getTransientAmount(0.3333)
            devOverTime = self.af.getTransientAmount(0.1)
            devOverTimeLong = self.af.getTransientAmount(1)
            dynamicsLong = self.af.getDynamics(0.5)
            dynamicsShort = self.af.getDynamics(0.06)
            loudestFreq = self.af.getLoudestFrequency()

            self.values = [sub, punch, lowmid, mid, highmid, highs, duration, median, average, spatialness, devOverTimeShort,
                          devOverTime, devOverTime2, devOverTimeLong, dynamicsLong, dynamicsShort, loudestFreq]
            # print("values:", self.values)

            # check if range is 0-1
            for i in range(len( self.values )):
                if self.values[i] > 1 or self.values[i] < 0:
                    # print("WARNING: Par out of range:", self.values[i], self.values[i])
                    raise ValueError("Par out of range:", self.parameters[i], " = ", self.values[i])

    def saveState(self, file):
        f_a = open(file, "a+")
        f_a.write("?" + self.af.path + "|" +
                  self.floatArrToString( self.values ) + "|" +
                  self.IDENTIFIER)
        f_a.close()

    def floatArrToString(self, arr):
        # convert float array to a string with values seperated by commas
        stringArr = ""
        for i in arr:
            stringArr += str(i) + ","
        stringArr = stringArr[:-1]
        return stringArr

    def printValues(self, arr):
        for i in range(len(arr)):
            str = "{: 0.2f}".format(arr[i])
            print( self.values[i], ": ", sep="", end="")
            print(str[0:5], ",", end="")
        print()