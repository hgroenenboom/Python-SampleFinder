import FileFinder
import GUI
import gc
import EuclideanDistance
import random
import AudioFile
import os

import numpy as np
import pyfftw

# debug variables, (for bypassing print statements)
DEBUG = False
count = 0

dataNames = "sub, punch, lowmid, mid, highmid, highs, duration, median, average, spatialness, devOverTimeShort, devOverTime, devOverTime2, devOverTimeLong, dynamicsLong, dynamicsShort, loudestFreq".split(", ")
def printDataArray(arr):

    for i in range(len(arr)):
        str = "{: 0.2f}".format(arr[i])
        print(dataNames[i], ": ", sep="", end="")
        print(str[0:5], ",", end="")
    print()

def floatArrToString(arr):
    # convert float array to a string with values seperated by commas
    stringArr = ""
    for i in arr:
        stringArr += str(i)+","
    stringArr = stringArr[:-1]
    return stringArr

def main():
    global DEBUG, count, dataNames

    # load all states from state file
    f_r = None
    loadedStates = None
    if(os.path.exists("states")):
        f_r = open("states", "r")
        loadedStates = f_r.read()

        # seperate individual audiofiles
        loadedStates = loadedStates.split("?")

        # seperate individual inputs
        contents2 = []
        for i in range(len(loadedStates)):
            c = loadedStates[i]
            contents2.append(c.split("|"))

        # seperate values
        loadedStates = []
        for i in contents2:
            if len(i) == 3:
                loadedStates.append([i[0], i[1].split(","), i[2]])
                #cast to float
                for j in range(len(loadedStates[len(loadedStates) - 1][1])):
                    loadedStates[len(loadedStates) - 1][1][j] = float(loadedStates[len(loadedStates) - 1][1][j])
        print("Amount of states found: ", len(loadedStates))


    # SELECT FOLDER TO SEARCH FROM FOR AUDIO FILES
    # J:/Dropbox/Muziek/Samples/Created/Overige/
    # J:/Dropbox/Muziek/Samples/
    # "J:/BackUp/17-09-11 Audio - Samples/Samples/Pro Tools Samples/"
    # "C:\\Program Files (x86)\\Image-Line\\FL Studio 11\\Data\\Patches\\Packs\\"
    # "J:\\BackUp\\17-09-11 Audio - Samples\\Samples\\Hip-Hop\\ArtyTorrent Pack 44-Hip Hop Drum Loops 100-109 bpm-WAV samples\\"
    # "J:\\Dropbox\\Muziek\\Samples\\Created\\Overige\\"
    # "J:\\BackUp\\17-09-11 Audio - Samples\\Samples\\Ethnic Percussion\\"
    # "J:\\BackUp\\17-09-11 Audio - Samples\\Samples\\Musicradar Realworld Drum Samples\\"
    # "J:\\Dropbox\\Muziek\\Samples\\Created\\Test Audio\\Noise"
    # "J:\\Dropbox\\Muziek\\Samples\\Created\\Test Audio\\", "J:\\Dropbox\\Muziek\\Samples\\Created\\Test Audio\\Sine"
    ff = FileFinder.FileFinder(["J:\\Dropbox\\Muziek\\Samples\\", "J:\\BackUp\\17-09-11 Audio - Samples\\Samples\\Musicradar Realworld Drum Samples\\", "J:/BackUp/17-09-11 Audio - Samples/Samples/Pro Tools Samples/", "J:/BackUp/17-09-11 Audio - Samples/Samples/808s_by_SHD", "J:/BackUp/17-09-11 Audio - Samples/Samples/Eigen Samples", "J:/BackUp/17-09-11 Audio - Samples/Samples/Timbales", "J:/BackUp/17-09-11 Audio - Samples/Samples/Ultimate Production Toolbox V1", "J:/BackUp/17-09-11 Audio - Samples/Samples/Cloudstorm Samples - Free Drums V1", "J:/BackUp/17-09-11 Audio - Samples/Samples/Drums Of War Samples", "J:/BackUp/17-09-11 Audio - Samples/Samples/Pro Tools Samples", "J:/BackUp/17-09-11 Audio - Samples/Samples/PrimeLoops DrumSamplesTaster 2012", "J:/BackUp/17-09-11 Audio - Samples/Samples/GSCW DRUMS Library Vol.1", "J:\\BackUp\\17-09-11 Audio - Samples\\Samples\\Ethnic Percussion\\"])
    #    , "J:\\BackUp\\17-09-11 Audio - Samples\\Samples\\Hip-Hop\\"
    #    , "J:/BackUp/17-09-11 Audio - Samples/Samples/Pro Tools Samples/"
    #
    #    , "J:\\BackUp\\17-09-11 Audio - Samples\\Samples\\Musicradar Realworld Drum Samples\\"
    # ])

    afStates = []
    totalSizeRead = 0

    # SEARCH FOR FILE IN STATE, identifier is used to make sure the state has the same encoding
    weigths = [3, 5, 5, 3, 3, 10, 2, 1, 3, 2, 3, 12.5, 12.5, 2, 25, 25, 50]
    for i in range(len(weigths)):
        weigths[i] *= 10
    # weigths = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    identifier = """sub = af.getMagnitudeForFrequencyRange(20, 100)
            punch = af.getMagnitudeForFrequencyRange(100, 300)
            lowmid = af.getMagnitudeForFrequencyRange(300, 500)
            mid = af.getMagnitudeForFrequencyRange(500, 1000)
            highmid = af.getMagnitudeForFrequencyRange(1000, 2000)
            highs = af.getMagnitudeForFrequencyRange(2000, 20000)
            duration = (af.duration / 100)**0.5
            median = af.getMedianAmp()
            average = af.getAverageAmp()
            spatialness = af.getSpatialness()
            devOverTimeShort = af.getTransientAmount(0.01)
            devOverTime2 = af.getTransientAmount(0.3333)
            devOverTime = af.getTransientAmount(0.1)
            devOverTimeLong = af.getTransientAmount(1)
            dynamicsLong = af.getDynamics(0.5)
            dynamicsShort = af.getDynamics(0.06)
            loudestFreq = af.getLoudestFreq()"""

    stateFound = False
    numStatesFound = 0
    for j in range(len(ff.audiofiles)):
        af = ff.audiofiles[j]
        if loadedStates is not None:
            for i in loadedStates:
                if i[0] == af.path and i[2] == identifier and af.stateLoaded is False:
                    if DEBUG:
                        print("stateFound: ", af.path, "\t wuth:", i[1])
                    afState = [af.path, i[1]]
                    afStates.append(afState)
                    totalSizeRead += af.size
                    af.stateLoaded = True
                    numStatesFound += 1
                    if DEBUG:
                        # print("\tafstates:", afStates)
                        print("state loaded")
    if loadedStates is not None:
        print("all saved states loaded:", numStatesFound)

    # GO THROUGH ALL AUDIOFILES FOUND, Either load from state, or calculate parameters and add to state
    print("Analyzing remaining audiofiles")
    for i in range(len(ff.audiofiles)):
        af = ff.audiofiles[i]

        # IF STATE IS NOT FOUND
        # generate state for current audio file
        # shorter then 5 seconds
        if af.stateLoaded is False and af.duration <= 15:
            afState = [af.path]

            if DEBUG or count % int(0.125*len(ff.audiofiles)) == 0:
                print("Starting with file: " + af.path)
                print("\tNum channels: " + str(af.channels))
                print("\tDuration: " + str(af.duration))

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

            numFreqElements = 6
            sub = af.getMagnitudeForFrequencyRange(20, 100)
            punch = af.getMagnitudeForFrequencyRange(100, 300)
            lowmid = af.getMagnitudeForFrequencyRange(300, 500)
            mid = af.getMagnitudeForFrequencyRange(500, 1000)
            highmid = af.getMagnitudeForFrequencyRange(1000, 2000)
            highs = af.getMagnitudeForFrequencyRange(2000, 20000)
            duration = af.getSigmoidDuration()
            median = af.getMedianAmp()
            average = af.getAverageAmp() #checked
            spatialness = af.getSpatialness() #checked
            devOverTimeShort = af.getTransientAmount(0.01)
            devOverTime2 = af.getTransientAmount(0.3333)
            devOverTime = af.getTransientAmount(0.1)
            devOverTimeLong = af.getTransientAmount(1)
            dynamicsLong = af.getDynamics(0.5)
            dynamicsShort = af.getDynamics(0.06)
            loudestFreq = af.getLoudestFrequency()
            # -> ParameterSet class maken met identifier in zich

            parameters = [sub, punch, lowmid, mid, highmid, highs, duration, median, average, spatialness, devOverTimeShort, devOverTime, devOverTime2, devOverTimeLong, dynamicsLong, dynamicsShort, loudestFreq]

            for j in range(len(parameters)):
                if parameters[j] > 1 or parameters[j] < 0:
                    print("WARNING: Par out of range:", dataNames[j], parameters[j])

            afState.append(parameters)
            afStates.append(afState)

            f_a = open("states", "a+")
            f_a.write("?"+af.path+"|"+
                      floatArrToString(parameters)+"|"+
                      identifier)
            f_a.close()

            totalSizeRead += af.size
            count = count + 1
            af.stateLoaded = True

            if DEBUG or count % int(0.125*len(ff.audiofiles)) == 0:
                print(afState)
                print()
                af.freeMem()
                gc.collect()

                print("\n<------------------------------------------------->")
                print("STATUS: ", 100 * totalSizeRead / ff.sizeOfAudiofiles, "%")
                GUI.my_gui.label['text'] = str(100 * totalSizeRead / ff.sizeOfAudiofiles) + "%" #werkt niet omdat gui achteraf pas wordt gebouwd :)
                print("<------------------------------------------------->\n")

    print("\n<---------------------------------------------------------------------------------------------------->\n")
    # EUCLIDEAN DISTANCES

    # create a list for calculating the euclidean distances (which holds only points)
    eucDistanceList = []
    for state in afStates:
        point = []
        for i in range(len(state[1])):
            point.append(state[1][i] * float(weigths[i]))
        # print(state[0], "\n\t", end="")
        # printDataArray(state[1])
        # print("\t", end="")
        # printDataArray(point)
        # print()
        eucDistanceList.append(point)

    # CREATE GUI CALLBACK, which will select a random audio file, and look for the most similar content.
    def guiNewAudioFiles():
        d = dataNames
        print(d)

        randint = random.randint(0, len(afStates))
        print("selected audiofile", randint)
        print(afStates[randint][0])
        s = afStates[randint][1]
        point = []
        for i in range(len(s)):
            # temporarally change values to see if lookup works
            # if d[i] == "spatialness":
            #     point.append(1.0 * float(weigths[i]))
            # elif d[i] == "loudestFreq":
            #     point.append(0.2+0.5*s[i] * float(weigths[i]))
            # else:
            point.append(s[i] * float(weigths[i]))
        print("\t", end="")
        printDataArray(point)
        print()
        GUI.my_gui.currentSample = afStates[randint][0]
        GUI.my_gui.w['text'] = GUI.my_gui.currentSample
        GUI.my_gui.play()

        closestPoints = EuclideanDistance.getPointIndicesSortedByClosest(point, eucDistanceList)
        GUI.my_gui.samplesSimilar = []
        GUI.my_gui.popupMenu['menu'].delete(0, 'end')

        for j in range(min(len(afStates), 20)):
            file = afStates[closestPoints[j]][0]
            print("\t", file)

            print("\t", end="")
            point = []
            s = afStates[closestPoints[j]][1]
            for i in range(len(s)):
                point.append(s[i] * float(weigths[i]))
            print("\t", end="")
            printDataArray(point)

            GUI.my_gui.samplesSimilar.append(file)
            # GUI.my_gui.popupMenu['menu'].add_command(label=file, command=GUI.my_gui.dropdownVar)

        for string in GUI.my_gui.samplesSimilar:
            GUI.my_gui.popupMenu['menu'].add_command(label=string,
                                                     command=lambda value=string:
                                                     GUI.my_gui.set_dropdown(value))
        print("\n")

    # ADD CALLBACK TO GUI, and start gui loop
    GUI.my_gui.greet_button['command'] = guiNewAudioFiles
    GUI.root.mainloop()


def testNormalization(len, chan):
    # TESTING THE NORMALIZATION OF pyfftw's rfft2
    # trying to find the best normalization
    length = len
    chan = chan

    x = (length-np.arange(length))/length #saw
    x = np.random.rand(length, chan) #noise

    # print("buffer length:", len(x))
    x = pyfftw.interfaces.numpy_fft.rfft2(x)  # pyfftw fft
    # print("buffer length:", len(x))
    x = np.absolute(x)

    # NORMALIZATION
    x /= length
    l = length

    # This part is calculated via power regression, via this website
    # https://planetcalc.com/5992/?xstring=1000000%2010000%201000%20100%2010%20400%202315425%20231542%2012512512%2050000%2090000%2020%2050%20150&ystring=724%2073%2023.365106790656302%208.354272021924835%203%2015.169374082802394%201102.0951586313518%20349.39964431734654%202560.287693649782%20162.97362932824748%20218.3%204.427518843176043%206.422129775837093%209.988181790695986&dolinear=1&doquadratic=1&dopower=1&docubic=1&doexponential=1&dologarithmic=1&dohyperbolic=1&doeexponential=1
    # this is a pretty amazing tool for function estimation in general
    y = 0.93334425065707260494 * l**0.48010607093436025172
    # Attemps with polynomial regression (https://arachnoid.com/polysolve/)
            # using different data point sets (exponential vs. linear)
            # low data values have worse outcomes with polynomial regression, this is due to the curvy form of a polynomial function
        # y = 3.3625540750294817e+001 * pow(l, 0) +  2.2210083690332055e-003 * pow(l, 1) + -4.4138535445393154e-009 * pow(l, 2) +  4.8944400005182634e-015 * pow(l, 3)+ -2.0327113713377099e-021 * pow(l, 4)+ -7.5581111250001365e-028 * pow(l, 5)+  1.2433448343968660e-033 * pow(l, 6)+ -6.1065218914381119e-040 * pow(l, 7)+  1.5340961651726406e-046 * pow(l, 8)+ -1.8136684373870868e-053 * pow(l, 9)+ -5.5878646300685812e-062 * pow(l, 10)+  2.0650459090895578e-067 * pow(l, 11)+  1.1312105629435023e-074 * pow(l, 12)+ -8.7818180318292125e-081 * pow(l, 13)+  1.1847358765871705e-087 * pow(l, 14)+ -7.0965593065000763e-095 * pow(l, 15)+  1.6662752270558232e-102 * pow(l, 16)
        # y = 1.2601647374892433e+001 * pow(l, 0)+  6.8008913681461315e-003 * pow(l, 1)+ -1.3673687165947163e-007 * pow(l, 2)+  1.7759971552807007e-012 * pow(l, 3)+ -1.3551447161590239e-017 * pow(l, 4)+  6.4054859864187708e-023 * pow(l, 5)+ -1.9456772984477435e-028 * pow(l, 6)+  3.8568686845378442e-034 * pow(l, 7)+ -5.0048091833057628e-040 * pow(l, 8)+  4.4198277291336512e-046 * pow(l, 9)+ -3.4375714598939627e-052 * pow(l, 10)+  3.4468206662119484e-058 * pow(l, 11)+ -3.0998160451156738e-064 * pow(l, 12)+  1.2751977364621651e-070 * pow(l, 13)+  3.4169910025533198e-077 * pow(l, 14)+ -5.0627335653931267e-083 * pow(l, 15)+  1.3224583536735571e-089 * pow(l, 16)
            #using very exponential data (int((1+i*0.003)**15), 2)
        # y = 9.4964679431860191e+000 * pow(l, 0)+  7.6107567154158132e-003 * pow(l, 1)+ -1.7581015888595541e-007 * pow(l, 2)+  2.5409057040738688e-012 * pow(l, 3)+ -2.1696443837687836e-017 * pow(l, 4)+  1.2034515135128238e-022 * pow(l, 5)+ -4.7851228140731669e-028 * pow(l, 6)+  1.4745090118002630e-033 * pow(l, 7)+ -3.5434844749425876e-039 * pow(l, 8)+  6.0206908646264732e-045 * pow(l, 9)+ -5.5585542717861106e-051 * pow(l, 10)+ -7.4381973535415025e-058 * pow(l, 11)+  7.9065307135048305e-063 * pow(l, 12)+ -7.5852545795460349e-069 * pow(l, 13)+  2.8044390327610238e-075 * pow(l, 14)+ -2.0562303591412954e-081 * pow(l, 15)+  3.9048514580442212e-087 * pow(l, 16)+ -3.9147634785740333e-093 * pow(l, 17)+ -8.8976817892744166e-100 * pow(l, 18)+  1.2419910748379180e-104 * pow(l, 19)+ -1.9694824568640377e-110 * pow(l, 20)+  1.3059916841064531e-116 * pow(l, 21)+ -3.2267528519482648e-123 * pow(l, 22);
    x /= y

    # print("x", x)
    x = np.squeeze(x)
    # print("x squeezed", x)
    # print("x Sum", np.sum(x))

    print(len, end=" ")
    print(np.sum(x))

def testCalibration2():
    length = 1000000
    chan = 1

    calibrateBuffer = np.random.rand(length, chan)
    calibrateBuffer = pyfftw.interfaces.numpy_fft.rfft(calibrateBuffer)  # pyfftw fft
    calibrateBuffer /= length #normalizing
    calibrateBuffer = np.absolute(calibrateBuffer)

    sr = 44100
    low = 0
    high = 5500

    lowestbin = round(low / (sr * 0.5) * length)
    highestbin = round(high / (sr * 0.5) * length)
    # scale = maxAmount * ( (highestbin-lowestbin) / lenOfFft )

    energyForFreqRange = np.sum(calibrateBuffer[lowestbin:highestbin])
    print(energyForFreqRange)

if __name__ == "__main__":
    # for i in range(0, 500):
    #     testNormalization(10+int((1+i*0.003)**15), 2)
    main()