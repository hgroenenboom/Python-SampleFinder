import os
import soundfile as sf
import numpy as np

DEBUG = False

class AudioFile:
    _extension = ""
    _size = 0
    path = ""
    abspath = ""
    soundfile = None
    channels = 0
    duration = 0
    numSamples = 0
    bitdepth = 0

    # private. DONT EDIT FROM OUTSIDE
    buffer = None
    samplerate = None

    stateLoaded = False

    def __init__(self, file):
        if DEBUG:
            print("loading audiofile:", file)

        if(os.path.exists(file)):
            self._extension = os.path.splitext(file)
            self._size = os.path.getsize(file)
            self.path = file
            self.abspath = os.path.abspath(file)

            info = sf.info(file)
            self.channels = info.channels
            self.duration = info.duration
            self.numSamples = info.frames
            self.samplerate = info.samplerate

            s = info.subtype
            if s == "PCM_16":
                self.bitdepth = 16
            elif s == "PCM_24":
                self.bitdepth = 24
            elif s == "FLOAT" or s == "PCM_32":
                self.bitdepth = 32
            else:
                raise Exception('unknown subtype:', s)

        else:
            print("Error file not found")

    def load(self):
        if DEBUG:
            print("loading file:", self.path)
        self._getWaveFile()
        self._stripSilence()

    def getBuffer(self):
        if self.buffer is not None:
            return self.buffer
        else:
            raise Exception('buffer not yet loaded')

    def _getWaveFile(self):
        # wavefile = wave.open(file)
        if self.soundfile is None:
            self.soundfile = sf.SoundFile(self.path)
        if self.buffer is None:
            self.buffer = self.soundfile.read()
            if DEBUG:
                print("Buffer max:", np.max(self.buffer))
                print("Buffer min:", np.min(self.buffer))

    def _stripSilence(self):
        # Get minimum amplitude to apply silence removal
        # min = np.min(np.abs(self.buffer))
        # ampOfminus40dB = self.getDBFs(min)
        # if ampOfminus40dB
        min = 0.0000001  # 0.001 # -60dBFs #TODO - make sure this doesnt wipe the whole audio. select minimum based on audio file.

        # get end frame of start noise
        foundNonNoiseAmplitude = False
        indexOfFoundSample = 0
        for i in range(len(self.buffer)):
            if not foundNonNoiseAmplitude:
                if abs(np.mean(self.buffer[i])) < 2 * min:
                    indexOfFoundSample = i
                else:
                    foundNonNoiseAmplitude = True
                    self.buffer = self.buffer[indexOfFoundSample:]
        self.numSamples = len(self.buffer)

        # get start frame of end noise
        foundNonNoiseAmplitude = False
        indexOfFoundSample = len(self.buffer) - 1
        for i in range(len(self.buffer)):
            j = len(self.buffer) - i - 1
            if not foundNonNoiseAmplitude:
                # print("amp at", j, " is", np.mean(self.buffer[j]))
                if abs(np.mean(self.buffer[j])) < 2 * min:
                    indexOfFoundSample = j
                else:
                    foundNonNoiseAmplitude = True

        # Set new buffer length without end noise
        self.buffer = self.buffer[:indexOfFoundSample]
        self.numSamples = len(self.buffer)
        self.duration = self.numSamples / float(self.samplerate)

