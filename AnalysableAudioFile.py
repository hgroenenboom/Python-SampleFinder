from AudioFile import AudioFile
import pyfftw
import math
import numpy as np
from threading import Thread

DEBUG = False

class AnalysableAudioFile(AudioFile):
    # hasAnalysisTools = True

    fft = None
    magFft = None
    monoMagFft = None

    def __init__(self, file):
        AudioFile.__init__(self, file)

    def _getDBFs(self, value):
        return 20 * math.log10( abs(value) )

    def _getFFT(self):
        self._getWaveFile()

        if self.fft is None:
            buffer = self.buffer
            if self.channels == 1:
                self.fft = pyfftw.interfaces.numpy_fft.rfft(buffer) #pyfftw fft
            else:
                try:
                    self.fft = pyfftw.interfaces.numpy_fft.rfft2(buffer) #pyfftw fft
                except:
                    print(buffer)
                    raise Exception(buffer, self.path)

        # delete DC
        self.fft = self.fft[1:]
        # delete conjugates
        self.fft = self.fft[ : int( 0.5*len(self.fft) ) ]

        return self.fft

    def _getFFTMagnitudes(self):
        self._getWaveFile()

        if self.magFft is None:
            #self.magFft = np.divide(self.getFFT(), self.numSamples) # normal normalization, doesn't work with MD arrays (stereo) -> created weird normalization :P
            fft = self._getFFT()

            if self.channels == 1:
                self.magFft = np.absolute(fft)
            else:
                self.magFft = np.absolute(fft)

            self.magFft /= self.numSamples

            #<---------------------------------------------------------------->
            # Weird normalization, since normal normalization doesnt work well
            if self.channels == 1:
                self.magFft *= 2
            elif self.channels == 2:
                l = self.numSamples
                y = 0.93334425065707260494 * l ** 0.48010607093436025172
                self.magFft /= y
            elif self.channels == 3:
                self.magFft *= 0.5
            elif self.channels == 4:
                self.magFft *= 0.3333
            elif self.channels == 5:
                self.magFft *= 0.25
            #<---------------------------------------------------------------->

            if self.channels is not 1:
                self.monoMagFft = np.delete(self.magFft, 1, 1)
                self.monoMagFft = np.squeeze(self.monoMagFft)
            else:
                self.monoMagFft = self.magFft
            if DEBUG:
                print("monoMagFft Sum", np.sum(self.monoMagFft))

        # check if data seems right
        # for i in range(10):
        #     print("end:", self.monoMagFft[len(self.monoMagFft) - (i + 1)], ", first:", self.monoMagFft[i])
        #     if self.monoMagFft[len(self.monoMagFft) - (i + 1)] == self.monoMagFft[i + 1]:
        #         print("same")
        # print()

        return self.monoMagFft

    def getMagnitudeForFrequencyRange(self, low, high):
        self._getWaveFile()

        self.monoMagFft = self._getFFTMagnitudes()

        # clip input
        low = min(0.5*self.samplerate, max(low, 0))
        high = min(0.5*self.samplerate, max(high, 0))
        lenOfFft = len(self.monoMagFft)

        lowestbin = round(low / (0.5*self.samplerate) * lenOfFft)
        highestbin = round(high / (0.5*self.samplerate) * lenOfFft)

        magForFreqRange = np.sum( self.monoMagFft[lowestbin:highestbin] )

        return self._sigmoid(magForFreqRange)

    def getDCOffset(self):
        return np.mean(self.buffer)

    def getAverageAmp(self):
        self._getWaveFile()

        averageAmp = np.abs( self.buffer )
        averageAmp = np.mean( averageAmp )
        averageAmp = np.subtract(averageAmp, self.getDCOffset())
        if(averageAmp < 0):
            print("averageAmp,", averageAmp)

        if self.getDCOffset() > 0.1:
            print("DC Offset, ", self.getDCOffset(), " at file:", self.path)
        return pow( averageAmp, 0.5 )

    def getSigmoidDuration(self):
        return self._sigmoid(self.duration)

    def getMedianAmp(self):
        self._getWaveFile()

        return pow( np.median( np.abs(self.buffer) ), 0.5)

    def freeMem(self):
        # Call this function to make sure memory is freed when the object is not used anymore

        if self.soundfile is not None:
            del self.soundfile
        if self.buffer is not None:
            del self.buffer
        if self.fft is not None:
            del self.fft
        if self.magFft is not None:
            del self.magFft
        if self.monoMagFft is not None:
            del self.monoMagFft
        if self.samplerate is not None:
            del self.samplerate

    def getSpatialness(self):
        spatialness = 0
        if(self.channels == 1):
            spatialness = 0
        elif self.channels > 1:
            averageAmp = np.mean( self.buffer, axis=1)

            diffAmp = []
            for i in range(len(averageAmp)):
                diffAmp.append( np.abs( np.subtract(averageAmp[i], self.buffer[i]) ) )

            diffAmp = np.mean( diffAmp ) * 0.5
            spatialness = diffAmp
            spatialness = spatialness / self.getAverageAmp()

        # print(spatialness)
        return self._sigmoid(spatialness)

    def getTransientAmount(self, seconds):
        numsteps = math.ceil(self.duration / seconds)

        stepsize = self.numSamples / numsteps
        energyPerMoment = []
        for i in range(numsteps):
            part = self.buffer[ int( stepsize * i ) : int( (i + 1) * stepsize ) ]
            average = np.mean( np.abs( part ) )
            # print("\taverage:\t", average)
            if average > 0.000001:
                energyPerMoment.append(0.05+average)

        amountOfMovement = 0
        for i in range(len(energyPerMoment)-1):
            amountOfMovement = amountOfMovement + abs( (energyPerMoment[i+1]) / energyPerMoment[i] - 1 )
        if len(energyPerMoment) == 1:
            amountOfMovement = energyPerMoment[0]

        amountOfMovement = amountOfMovement / len(energyPerMoment)

        return self._sigmoid(amountOfMovement)

    def getDynamics(self, seconds):
        numsteps = math.ceil(self.duration / seconds)

        stepsize = self.numSamples / numsteps
        energyPerMoment = []
        for i in range(numsteps):
            part = self.buffer[ int( stepsize * i ) : int( (i + 1) * stepsize ) ]
            average = np.mean( np.abs( part ) )
            if average > 0.000001:
                energyPerMoment.append(0.05+average)

        averageEnergy = np.mean(energyPerMoment)

        dynamic = 0
        if len(energyPerMoment) == 1:
            dynamic = energyPerMoment[0]
        elif len(energyPerMoment) > 1:
            for i in range(len(energyPerMoment)):
                dynamic = dynamic + abs( averageEnergy - energyPerMoment[i] )

                dynamic = dynamic / len(energyPerMoment)

        return self._sigmoid(dynamic / seconds)

    def getLoudestFrequency(self):
        self._getFFTMagnitudes()

        if self.monoMagFft is not None:
            if DEBUG:
                print("path,", self.path)
                print("\tnumchannels,", self.channels)
                print("\tlength of monoMagFft,", len(self.monoMagFft))
            index_max = max(range(len(self.monoMagFft)), key=self.monoMagFft.__getitem__)
            freq = float(index_max) / len(self.monoMagFft)
            if DEBUG:
                print("\tloudest freq: ", freq)
                print()

            return pow(freq, 0.5)

    def _sigmoid(self, val):
        return val / (1 + abs(val))