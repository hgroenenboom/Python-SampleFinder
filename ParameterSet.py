import AnalysableAudioFile

# TODO
            # -> ParameterSet class maken met identifier in zich
            # ParameterSet {
            #   ParameterSet(AnalysableAudioFile, shouldSaveState=False, isLoadedFromFile, stateID="") ->  fill "set" struct and check if state should be saved to disk.
            #   struct set {
            #       string[] parameters
            #       string identifier (parameters as single string + stateID)
            #       float[] values
            #   }
            # }

class ParameterSet:
    isLoadedFromFile = False
    isGenerated = False

    af = None
    STATEID = ""
    # string list
    PARAMETERS = "sub, punch, lowmid, mid, highmid, highs, duration, median, average, spatialness, devOverTimeShort, devOverTime, devOverTime2, devOverTimeLong, dynamicsLong, dynamicsShort, loudestFreq".split(", ")
    identifier = "" # parameters as single string + identifier
    values = [] # float list

    def __init__(self, analysableaudiofile, values=None, stateID=""):
        self.STATEID = stateID
        self.identifier = self.PARAMETERS + self.STATEID
        self.af = analysableaudiofile

        if values is not None:
            self.values = values
            self.isLoadedFromFile = True

    def generateState(self):
        if self.values is None:
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

            # check if range is 0-1
            for i in range(len( self.values )):
                if self.values[i] > 1 or self.values[i] < 0:
                    # print("WARNING: Par out of range:", self.values[i], self.values[i])
                    raise ValueError("Par out of range:", self.parameters[i], " = ", self.values[i])

    def saveState(self, file):
        f_a = open("states", "a+")
        f_a.write("?" + self.af.path + "|" +
                  self.floatArrToString( self.values ) + "|" +
                  self.identifier)
        f_a.close()

    def floatArrToString(arr):
        # convert float array to a string with values seperated by commas
        stringArr = ""
        for i in arr:
            stringArr += str(i) + ","
        stringArr = stringArr[:-1]
        return stringArr