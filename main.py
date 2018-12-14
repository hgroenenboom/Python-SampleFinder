import gc
import random
import os
import numpy as np
import pyfftw

import FileFinder
import GUI
import EuclideanDistance
from ParameterSet import ParameterSet


# debug variables, (for bypassing print statements)
DEBUG = False
count = 0

def getAudioFiles():
    # SELECT FOLDER TO SEARCH FROM FOR AUDIO FILES
    mainFolder = "S:/Audio/Audio - Samples/Samples/"
    dropboxFolder = "C:/Users/HAROL/Dropbox/"

    def getSamplesDirsFromMainFolder():
        subfolders = os.listdir(mainFolder);
        toRemove = []
        for i in range(len(subfolders)):
            if not os.path.isdir(mainFolder + subfolders[i]):
                toRemove.append(i)
            else:
                subfolders[i] = mainFolder + subfolders[i]

        toRemove.reverse()
        for i in toRemove:
            subfolders.remove(subfolders[i])

        print(subfolders)
        return subfolders

    sampleDirs = []
    for i in getSamplesDirsFromMainFolder():
        sampleDirs.append(i)
    sampleDirs.append(dropboxFolder + "Muziek/Samples/")
    # ff = FileFinder.FileFinder([dropboxFolder + "Muziek/Samples/", dropboxFolder + "Muziek/Samples/",
    #                             mainFolder + "Musicradar Realworld Drum Samples/", mainFolder + "Pro Tools Samples/",
    #                             mainFolder + "808s_by_SHD", mainFolder + "Eigen Samples", mainFolder + "Timbales",
    #                             mainFolder + "Ultimate Production Toolbox V1",
    #                             mainFolder + "Cloudstorm Samples - Free Drums V1", mainFolder + "Drums Of War Samples",
    #                             mainFolder + "Pro Tools Samples", mainFolder + "PrimeLoops DrumSamplesTaster 2012",
    #                             mainFolder + "GSCW DRUMS Library Vol.1", mainFolder + "Ethnic Percussion/"])
    ff = FileFinder.FileFinder(sampleDirs)
    return ff

def main():
    global DEBUG, count

    # Weights
    weigths = [500000/10, 500000/10, 500000/10, 500000/10, 500000/10, 500000/2, 500000, 1, 500000/3, 2, 3, 12.5, 12.5, 2, 500000, 500000, 500000]
    for i in range(len(weigths)):
        weigths[i] *= 0.1
    # weigths = [1, 1, 1, 1, 1, 1, 10000, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # weigths = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    for i in range(len(weigths)):
        GUI.my_gui.createWeigthWidget( ParameterSet.PARAMETERS[i], weigths, i)

    # FileFinder object containing a list of all imported audio files
    ff = getAudioFiles()
    # List to contain all parameters
    parameterSets = []
    totalSizeRead = 0

    print("\n<---------------------------------------------------------------------------------------------------->\n")
    print("Loading saved states:")

    # load all states from state file
    f_r = None
    loadedStates = None
    if(os.path.exists("states")):
        f_r = open("states", "r")
        loadedStates = f_r.read()

        # seperate individual audiofiles (seperator=?)
        loadedStates = loadedStates.split("?")

        # seperate individual inputs (seperator=|)
        contents2 = []
        for i in range(len(loadedStates)):
            c = loadedStates[i]
            contents2.append(c.split("|"))

        # seperate values (seperator=,)
        loadedStates = []
        for i in contents2:
            if len(i) == 3:
                loadedStates.append([i[0], i[1].split(","), i[2]])
                # cast values to float
                for j in range( len( loadedStates[0][1] ) ):
                    loadedStates[ len(loadedStates) - 1 ][1][j] = float( loadedStates[ len(loadedStates) - 1 ][1][j])
        print("Amount of states found: ", len(loadedStates))
    else:
        print("\tStates file does not exist!")

    # load states
    numStatesFound = 0
    for af in ff.audiofiles:
        if loadedStates is not None:
            for s in loadedStates:
                if s[0] == af.path and s[2] == ParameterSet.IDENTIFIER and af.stateLoaded is False:
                    if DEBUG:
                        print("stateFound: ", af.path, "\t with:", s[1])
                    parameterSets.append( ParameterSet( af, s[1] ) )
                    totalSizeRead += af._size
                    af.stateLoaded = True
                    numStatesFound += 1
                    if DEBUG:
                        # print("\tafstates:", afStates)
                        print("state loaded")
    if loadedStates is not None:
        print("\tall saved states loaded:", numStatesFound)

    print("\n<---------------------------------------------------------------------------------------------------->\n")


    # GO THROUGH ALL AUDIOFILES FOUND, Either load from state, or calculate parameters and add to state
    print("Analyzing remaining audiofiles:", len(ff.audiofiles) - numStatesFound)

    totalSizeToRead = 0
    for i in range( len(ff.audiofiles) ):
        # print(af.stateLoaded )
        if af.stateLoaded == False and af.duration <= 15 and af.duration >= 0.001:
            totalSizeToRead += af._size
    print("Total size to read:", totalSizeToRead)

    totalSizeRead = 0
    for i in range(len(ff.audiofiles)):
        af = ff.audiofiles[i]

        # IF STATE IS NOT FOUND
        # generate state for current audio file
        # shorter then 5 seconds
        if af.stateLoaded is False and af.duration <= 15 and af.duration >= 0.001:
            if DEBUG or count % int(0.125*len(ff.audiofiles)) == 0:
                print("Starting with file: " + af.path)
                print("\tNum channels: " + str(af.channels))
                print("\tDuration: " + str(af.duration))

            newSet = ParameterSet( af )
            newSet.generateState()
            parameterSets.append(newSet)
            newSet.saveState("states")

            totalSizeRead += af._size
            count = count + 1
            af.stateLoaded = True

            if DEBUG or count % int(0.01*len(ff.audiofiles)) == 0:
                print(newSet)
                print()

                af.freeMem()
                gc.collect()

                print("\n<------------------------------------------------->")
                print("STATUS: ", 100 * totalSizeRead / totalSizeToRead, "%", end="")
                print("\t files read:", i, "of total num files:", len(ff.audiofiles) - numStatesFound)
                GUI.my_gui.label['text'] = str(100 * totalSizeRead / totalSizeToRead) + "%" #werkt niet omdat gui achteraf pas wordt gebouwd :)
                print("<------------------------------------------------->\n")

    print("\n<---------------------------------------------------------------------------------------------------->\n")
    # EUCLIDEAN DISTANCES

    # create a list for calculating the euclidean distances (which holds only points)


    eucDistanceList = []

    def calcEuclideanDistanceList(eucDistanceList, sets, weigths):
        del eucDistanceList[:]
        for s in sets:
            point = []
            for i in range( len( s.values ) ):
                point.append( float(weigths[i]) * s.values[i] )
            # print(state[0], "\n\t", end="")
            # printDataArray(state[1])
            # print("\t", end="")
            # printDataArray(point)
            # print()
            eucDistanceList.append( point )

    # CREATE GUI CALLBACK, which will select a random audio file, and look for the most similar content.
    def guiNewAudioFiles():
        d = ParameterSet.PARAMETERS
        print(d)

        randint = random.randint( 0, len( parameterSets ) )
        print("selected audiofile", randint)
        print( parameterSets[randint].af.path )
        values = parameterSets[randint].values

        point = []
        for i in range( len(values) ):
            # temporarally change values to see if lookup works
            # if d[i] == "spatialness":
            #     point.append(1.0 * float(weigths[i]))
            # elif d[i] == "loudestFreq":
            #     point.append(0.2+0.5*s[i] * float(weigths[i]))
            # else:
            point.append(values[i] * float(weigths[i]))
        print("\t", end="")
        # printDataArray(point)
        # print()
        # GUI.my_gui.createParameterEntrys(dataNames, point)

        GUI.my_gui.currentAudioFile = parameterSets[randint].af
        GUI.my_gui.w['text'] = GUI.my_gui.currentAudioFile.path
        # GUI.my_gui.play()

        calcEuclideanDistanceList(eucDistanceList, parameterSets, weigths)
        closestPoints = EuclideanDistance.getPointIndicesSortedByClosest(point, eucDistanceList)
        GUI.my_gui.similarAudioFiles = []
        GUI.my_gui.popupMenu['menu'].delete(0, 'end')

        # add similar samples to GUI
        for j in range( min( len( parameterSets ), 20) ):
            s = parameterSets[closestPoints[j]]
            print("\t", s.af.path)

            print("\t", end="")
            point = []
            values = parameterSets[closestPoints[j]].values
            for i in range(len(values)):
                point.append( float(weigths[i]) * values[i] )
            print("\t", end="")
            # printDataArray(point)

            GUI.my_gui.similarAudioFiles.append( s.af )
            # GUI.my_gui.popupMenu['menu'].add_command(label=file, command=GUI.my_gui.dropdownVar)

        for i in range(len(GUI.my_gui.similarAudioFiles)):
            string = GUI.my_gui.similarAudioFiles[i].path
            GUI.my_gui.popupMenu['menu'].add_command(label=string,
                                                     command=lambda value=string:
                                                     GUI.my_gui.set_dropdown(value))
            # instantly play sample
            # if i < 5:
            #     GUI.my_gui.playSample(GUI.my_gui.similarAudioFiles[i])
        GUI.my_gui.playMultiple()
        print("\n")

    print("Finished loading!")

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