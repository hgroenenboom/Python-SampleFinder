from AudioFile import AudioFile

class AnalysableAudioFile(AudioFile):
    def __init__(self, file):
        AudioFile.__init__(file)