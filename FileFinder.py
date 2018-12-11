from os.path import splitext
import os
import AudioFile

# TODO
# - Delete/skip duplicate files

class FileFinder:
    audiofiles = []
    sizeOfAudiofiles = 0
    maxduration = 2

    def isPathAdded(self, path):
        isAdded = False
        for p in self.audiofiles:
            if p == path:
                isAdded = True
        return isAdded

    def __init__(self, directories):
        errorsFound = False
        print("FileFinder - searching for files")
        # all userinputted dirs
        for directory in directories:
            # get all files in input dir
            if os.path.exists(directory):
                print("\tcurrent dir:", directory)
            else:
                print("ERROR: dir", directory, " not found!")
            num_files = 0
            max_files = 200
            for root, dir, files in os.walk(directory):
                # check every file and add to list
                for file in files:
                    if num_files < max_files:
                        _, ext = splitext(file)
                        if ext == ".wav" and not self.isPathAdded(root+"/"+file):
                            af = None
                            try:
                                af = AudioFile.AudioFile(root+"/"+file)
                                if(af.duration < self.maxduration):
                                    self.audiofiles.append(af)
                                    self.sizeOfAudiofiles += af.size
                                    num_files += 1
                            except Exception as e:
                                errorsFound = True
                                # print("\t\t", e)
                    elif max_files == num_files:
                        num_files += 1
                        print("\t\tfile limit of folder exceeded, limit is", max_files, "files")


        if errorsFound:
            print("\t\t ERROR - some errors occured while reading the sound files")

        print("FileFinder - files found:", len(self.audiofiles))