from os.path import splitext
import os
import AnalysableAudioFile

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
            if os.path.exists(directory):
                print("\tcurrent dir:", directory)
            else:
                print("ERROR: dir", directory, " not found!")
            num_files = 0
            max_files = 500
            for root, dir, files in os.walk(directory):
                # check every file and add to list
                for file in files:
                    if num_files < max_files:
                        _, ext = splitext(file)
                        if ext == ".wav": #and not self.isPathAdded(root+"/"+file):
                            af = None
                            try:
                                af = AnalysableAudioFile.AnalysableAudioFile(root+"/"+file)
                                if(af.duration < self.maxduration):
                                    self.audiofiles.append(af)
                                    self.sizeOfAudiofiles += af._size
                                    num_files += 1
                            except Exception as e:
                                errorsFound = True
                                # print("\t\t", e)
                        else:
                            num_files += 1
                    elif max_files == num_files:
                        num_files += 1
                        print("\t\tfile limit of folder exceeded, limit is", max_files, "files")
                        break;

        if errorsFound:
            print("\t\t ERROR - some errors occured while reading the sound files")

        print("FileFinder - files found:", len(self.audiofiles))
        print("deleted duplicates:", self.deleteDuplicates())
        print("FileFinder - files read:", len(self.audiofiles))

    # used this function at the end to delete duplicates
    def isPathAdded(self, path):
        isAdded = False
        a = os.path.abspath(path)
        for p in self.audiofiles:
            b = p.abspath
            if a is b:
                isAdded = True
                # print("true")
        return isAdded

    def deleteDuplicates(self, numdeletedfiles=0):
        isDeleted = False
        markedIndices = []
        for i in range(len(self.audiofiles)):
            af = self.audiofiles[i]
            found = False
            for j in range(i + 1, len(self.audiofiles)):
                if not found:
                    af2 = self.audiofiles[j]
                    if af.abspath == af2.abspath:
                        markedIndices.append(j)
                        found = True

        markedIndices.sort()
        markedIndices.reverse()
        # print(markedIndices)
        for i in markedIndices:
            self.audiofiles.remove(self.audiofiles[i])

        return len(markedIndices)