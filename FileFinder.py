from os.path import splitext
import os
import soundfile

import AudioFile

class FileFinder:
    audiofiles = []
    sizeOfAudiofiles = 0
    maxduration = 2

    def __init__(self, directories):
        errorsFound = False
        print("FileFinder - searching for files")
        # all userinputted dirs
        for directory in directories:
            # get all files in input dir
            for root, dir, files in os.walk(directory):
                # check every file and add to list
                for file in files:
                    _, ext = splitext(file)
                    if ext == ".wav":
                        af = None
                        try:
                            af = AudioFile.AudioFile(root+"/"+file)
                            if(af.duration < self.maxduration):
                                self.audiofiles.append(af)
                                self.sizeOfAudiofiles += af.size
                        except Exception as e:
                            errorsFound = True
                            print(e)

        if errorsFound:
            print("\t ERROR - some errors occured while reading the sound files")

        print("FileFinder - files found:", len(self.audiofiles))