from tkinter import Tk, Label, Button, StringVar, OptionMenu, Frame, Entry, END, LEFT, TOP
import tkinter as tk
import winsound
from threading import Thread
import random
import simpleaudio as sa
import numpy as np
import time

class MyGUI:
    currentAudioFile = ""
    similarAudioFiles = ["swag", "lol"]
    back = None
    f = None
    paramEntrys = None

    def __init__(self, master):
        self.master = master

        # import simpleaudio.functionchecks as fc
        # fc.LeftRightCheck.run()

        master.title("A simple GUI")
        master.geometry("1000x1000")  # You want the size of the app to be 500x500
        #master.resizable(0, 0)  # Don't allow resizing in the x or y direction
        master.option_add("*Button.Background", "black")
        master.option_add("*Button.Foreground", "red")

        back = Frame(master=master, bg='blue')
        back.pack_propagate(0) # dont allow widgets to resize frame
        back.pack(fill=tk.BOTH, expand=1)
        self.back = back

        self.label = Label(back, text="This is our first GUI!")
        self.label.pack()

        self.greet_button = Button(back, text="set new samples")
        self.greet_button.pack()

        self.w = Label(back, text=" ... ")
        self.w.pack()
        self.play_button = Button(back, text="Play", command=self.play)
        self.play_button.pack()
        self.play_button = Button(back, text="Play multiple", command=self.playMultiple)
        self.play_button.pack()


        self.dropdownVar = StringVar()
        self.dropdownVar.set(self.similarAudioFiles[0])
        self.popupMenu = OptionMenu(back, self.dropdownVar, *self.similarAudioFiles)
        self.popmenLabel = Label(back, text="Choose similar sample")
        self.popmenLabel.pack()
        self.popupMenu.pack()
        # self.dropdownVar.trace('w', self.change_dropdown)

        self.play_button2 = Button(back, text="Play", command=self.play2)
        self.play_button2.pack()

        self.close_button = Button(back, text="Close", command=master.quit)
        self.close_button.pack()

    def playMultiple(self):
        self.play()
        time.sleep(self.currentAudioFile.duration)
        for i in range(5):
            self.playSample(self.similarAudioFiles[i])
            time.sleep(self.similarAudioFiles[i].duration)

    def play(self):
        self.playSample(self.currentAudioFile)

    def play2(self):
        af = None
        for i in range( len(self.similarAudioFiles) ):
            if self.similarAudioFiles[i].path == self.dropdownVar.get():
                af = self.similarAudioFiles[i]
        self.playSample( af )

    def playSample(self, audiofileObj):
        def p(f):
            # print(f)
            f.load()
            b = f.getBuffer().copy()
            b *= 32767
            b = b.astype( np.int16 )

            # print(f.channels)
            # print(b.shape)
            wave_obj = sa.WaveObject(b, f.channels, 2, f.samplerate)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        thread = Thread(target=lambda f=audiofileObj: p(f), args=(audiofileObj,))
        # thread = Thread(target=lambda f=audiofileObj: winsound.PlaySound(f.path, winsound.SND_FILENAME), args=(audiofileObj,))
        thread.start()

    def change_dropdown(self, *args):
        print("change dropdown")
        print(self.dropdownVar.get())
        self.play2()

    def set_dropdown(self, string):
        print("set dropdown")
        if string is self.dropdownVar.get():
            pass
        if string is not self.dropdownVar.get():
            self.dropdownVar.set(string)
            self.play2()

    def createWeigthWidget(self, text, weights, index):
        if(self.f is None):
            color = ["red", "orange", "yellow", "green", "blue", "violet"]
            self.f = []
            for i in range(len(weights)):
                self.f.append( Frame( master=self.back, bg=random.choice(color) ) )
                self.f[index].pack()
            # print(self.f)
        def setToWeight(e):
            weights[index] = float(entry.get())

        self.label = Label(self.f[0], text=text)
        self.label.grid( row=index%4*2, column=int( index/4 ), padx=5, pady=5 )
        entry = Entry(self.f[0])
        entry.bind("<KeyRelease>", setToWeight)
        entry.insert( END, weights[index] )
        entry.grid( row=index%4*2+1, column=int( index/4 ), padx=5 )


    # def createParameterEntrys(self, ids, params):
    #     if (self.f is None):
    #         self.f = [Frame(master=self.back, bg='blue')] * len(params)
    #
    #     for i in range(len(params)):
    #         if self.paramEntrys is None:
    #             self.paramEntrys = Entry(self.f[i])
    #
    #         def setToWeight(e):
    #             params[i] = float(self.paramEntrys[i].get())
    #
    #         self.label = Label( self.f[i], text=ids[i])
    #         self.label.pack( side=LEFT )
    #         self.paramEntrys[i].bind("<Return>", setToWeight)
    #         self.paramEntrys[i].insert(END, params[i])
    #         self.paramEntrys[i].pack( side=LEFT )
    #         self.f[i].pack()

root = Tk()
my_gui = MyGUI(root)