import FileFinder
import GUI
import gc
import EuclideanDistance
import random
import AudioFile

import numpy as np
import pyfftw

DEBUG = False
count = 0

def main():
    global DEBUG, count

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
    ff = FileFinder.FileFinder(["J:\\Dropbox\\Muziek\\Samples\\", "J:\\BackUp\\17-09-11 Audio - Samples\\Samples\\Musicradar Realworld Drum Samples\\", "J:/BackUp/17-09-11 Audio - Samples/Samples/Pro Tools Samples/", "J:/BackUp/17-09-11 Audio - Samples/Samples/808s_by_SHD", "J:/BackUp/17-09-11 Audio - Samples/Samples/Cloudstorm Samples - Free Drums V1", "J:/BackUp/17-09-11 Audio - Samples/Samples/J:\BackUp\17-09-11 Audio - Samples\Samples\GSCW DRUMS Library Vol.1"])
                                #    , "J:\\BackUp\\17-09-11 Audio - Samples\\Samples\\Hip-Hop\\"
                                #    , "J:/BackUp/17-09-11 Audio - Samples/Samples/Pro Tools Samples/"
                                #
                                #    , "J:\\BackUp\\17-09-11 Audio - Samples\\Samples\\Musicradar Realworld Drum Samples\\"
                                # ])

    afStates = []
    totalSizeRead = 0

    # get average amount of subbass
    for i in range(len(ff.audiofiles)):
        af = ff.audiofiles[i]
        # generate state for current audio file
            # shorter then 20 seconds
        if af.stateLoaded is False and af.duration <= 5:
            afState = [af.path]

            if DEBUG or count % 20 == 0:
                print("Starting with file: " + af.path)
                print("\tNum channels: " + str(af.channels))
                print("\tDuration: " + str(af.duration))

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

            numFreqElements = 6
            sub = af.getMagnitudeForFrequencyRange(20, 100) / numFreqElements * 2
            punch = af.getMagnitudeForFrequencyRange(100, 300) / numFreqElements * 2
            lowmid = af.getMagnitudeForFrequencyRange(300, 500) / numFreqElements * 2
            mid = af.getMagnitudeForFrequencyRange(500, 1000) / numFreqElements * 2
            highmid = af.getMagnitudeForFrequencyRange(1000, 2000) / numFreqElements * 2
            highs = af.getMagnitudeForFrequencyRange(2000, 20000) / numFreqElements * 0.5
            duration = (af.duration / 100)**0.5 * 3
            median = af.getMedianAmp() * 2
            average = af.getAverageAmp()
            spatialness = af.getSpatialness() * 0.5
            devOverTimeShort = af.getDevelopmentOverTime(0.01) * 100
            devOverTime = af.getDevelopmentOverTime(0.1) * 100
            devOverTimeLong = af.getDevelopmentOverTime(1) * 100

            # afState.append([sub4, sub3, sub2, sub, punch, lowmid, mid, highmid, highs, lows])
            afState.append([sub, punch, lowmid, mid, highmid, highs, duration, median, average, spatialness, devOverTimeShort, devOverTime, devOverTimeLong])
            afStates.append(afState)

            totalSizeRead += af.size

            if DEBUG or count % 20 == 0:
                print(afState)
                print()
                af.freeMem()
                gc.collect()

                print("\n<------------------------------------------------->")
                print("STATUS: ", 100 * totalSizeRead / ff.sizeOfAudiofiles, "%")
                GUI.my_gui.label['text'] = str(100 * totalSizeRead / ff.sizeOfAudiofiles) + "%"
                print("<------------------------------------------------->\n")

            count = count + 1

    print("\n<---------------------------------------------------------------------------------------------------->\n")

    # create a list for calculate the euclidean distance (which holds only points)
    eucDistanceList = []
    for state in afStates:
        eucDistanceList.append(state[1])

    def guiNewAudioFiles():
        randint = random.randint(0, len(afStates))
        print("selected audiofile", randint)
        print(afStates[randint][0])
        print(afStates[randint][1], "\n")
        GUI.my_gui.currentSample = afStates[randint][0]
        GUI.my_gui.w['text'] = GUI.my_gui.currentSample

        closestPoints = EuclideanDistance.getPointIndicesSortedByClosest(eucDistanceList[randint], eucDistanceList)
        GUI.my_gui.samplesSimilar = []
        GUI.my_gui.popupMenu['menu'].delete(0, 'end')

        for j in range(min(len(afStates), 10)):
            file = afStates[closestPoints[j]][0]
            print("\t", file)
            print("\t", afStates[closestPoints[j]][1])
            GUI.my_gui.samplesSimilar.append(file)
            # GUI.my_gui.popupMenu['menu'].add_command(label=file, command=GUI.my_gui.dropdownVar)

        for string in GUI.my_gui.samplesSimilar:
            GUI.my_gui.popupMenu['menu'].add_command(label=string,
                             command=lambda value=string:
                             GUI.my_gui.dropdownVar.set(value))
        print("\n")

    GUI.my_gui.greet_button['command'] = guiNewAudioFiles

    GUI.root.mainloop()


def testNormalization():
    length = 12525
    chan = 2
    x = (length-np.arange(length))/length
    x = np.random.rand(length, chan)
    # print("x:", x)
    print("buffer length:", len(x))
    x = pyfftw.interfaces.numpy_fft.rfft2(x)  # pyfftw fft
    # print("x na fft: ", x)
    print("buffer length:", len(x))
    x = np.absolute(x)

    x /= length

    # This part is calculated via power regression, via this website
    # https://planetcalc.com/5992/?xstring=1000000%2010000%201000%20100%2010%20400%202315425%20231542%2012512512%2050000%2090000%2020%2050%20150&ystring=724%2073%2023.365106790656302%208.354272021924835%203%2015.169374082802394%201102.0951586313518%20349.39964431734654%202560.287693649782%20162.97362932824748%20218.3%204.427518843176043%206.422129775837093%209.988181790695986&dolinear=1&doquadratic=1&dopower=1&docubic=1&doexponential=1&dologarithmic=1&dohyperbolic=1&doeexponential=1
    # this is a pretty amazing tool for function estimation in general
    l = length
    y = 0.93334425065707260494 * l**0.48010607093436025172
    x /= y

    print("x", x)
    x = np.squeeze(x)
    print("x", x)
    print("x Sum", np.sum(x))

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
    # testNormalization()
    main()