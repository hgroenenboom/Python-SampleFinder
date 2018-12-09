import os
import soundfile as sf
import numpy as np
import pyfftw

class AudioFile:
    extension = ""
    size = 0
    path = ""
    soundfile = None
    channels = 0
    duration = 0
    numSamples = 0

    buffer = None
    fft = None
    magFft = None
    monoMagFft = None
    samplerate = None

    stateLoaded = False

    def __init__(self, file):
        if(os.path.exists(file)):
            self.extension = os.path.splitext(file)
            self.size = os.path.getsize(file)
            self.path = file
            self.channels = sf.info(file).channels
            self.duration = sf.info(file).duration
            self.numSamples = sf.info(file).frames
            self.samplerate = sf.info(file).samplerate
        else:
            print("Error file not found")

    def getWaveFile(self):
        # wavefile = wave.open(file)
        if self.soundfile is None:
            self.soundfile = sf.SoundFile(self.path)
        if self.buffer is None:
            self.buffer = self.soundfile.read()
            print("Buffer max:", np.max(self.buffer))
            print("Buffer min:", np.min(self.buffer))

    def getFFT(self):
        self.getWaveFile()

        if self.fft is None:
            buffer = self.buffer
            if self.channels == 1:
                self.fft = pyfftw.interfaces.numpy_fft.rfft(buffer) #pyfftw fft
            else:
                self.fft = pyfftw.interfaces.numpy_fft.rfft2(buffer) #pyfftw fft

        return self.fft

    def getFFTMagnitudes(self):
        self.getWaveFile()

        if self.magFft is None:
            #self.magFft = np.divide(self.getFFT(), self.numSamples) # normal normalization, doesn't work with MD arrays (stereo) -> created weird normalization :P
            fft = self.getFFT()

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
            print("monoMagFft Sum", np.sum(self.monoMagFft))

        return self.monoMagFft

    def getMagnitudeForFrequencyRange(self, low, high):
        self.getWaveFile()

        self.monoMagFft = self.getFFTMagnitudes()

        # clip input
        low = min(0.5*self.samplerate, max(low, 0))
        high = min(0.5*self.samplerate, max(high, 0))
        lenOfFft = len(self.monoMagFft)

        lowestbin = round(low / (0.5*self.samplerate) * lenOfFft)
        highestbin = round(high / (0.5*self.samplerate) * lenOfFft)

        magForFreqRange = np.sum( self.monoMagFft[lowestbin:highestbin] )

        return magForFreqRange

    def getAverageAmp(self):
        self.getWaveFile()

        averageAmp = self.buffer
        if(self.channels > 1):
            averageAmp = np.mean( np.power( np.abs(self.buffer), 2.0 ), axis=1)
        averageAmp = sum(averageAmp) / len(averageAmp)

        return averageAmp

    def getMedianAmp(self):
        self.getWaveFile()

        return np.median( np.abs(self.buffer) )

    def freeMem(self):
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

        # print(spatialness)
        return spatialness

    def getDevelopmentOverTime(self):
        numsteps = 100

        stepsize = self.numSamples / numsteps
        energyPerMoment = []
        for i in range(numsteps):
            part = self.buffer[ int( stepsize * i ) : int( (i + 1) * stepsize ) ]
            average = np.mean( np.abs( part ) )
            # print("\taverage:\t", average)
            if average > 0.000001:
                energyPerMoment.append(average)

        amountOfMovement = 0
        for i in range(len(energyPerMoment)-1):
            amountOfMovement = amountOfMovement + abs( (0.0000001+energyPerMoment[i+1]) / energyPerMoment[i])

        amountOfMovement = amountOfMovement / len(energyPerMoment)

        # print("Length of energyPerMovement:\t", len(energyPerMoment))
        # print("Amount of movement:\t", amountOfMovement, self.path)
        return amountOfMovement
