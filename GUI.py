from tkinter import Tk, Label, Button, StringVar, OptionMenu, Frame, Entry, END, LEFT, TOP
import tkinter as tk
import subprocess
import os
import winsound
from threading import Thread
import random

class MyGUI:
    currentSample = ""
    samplesSimilar = [ "swag", "lol" ]
    back = None
    f = None
    paramEntrys = None

    def __init__(self, master):
        self.master = master
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
        self.dropdownVar.set(self.samplesSimilar[0])
        self.popupMenu = OptionMenu(back, self.dropdownVar, *self.samplesSimilar)
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
        for i in range(5):
            self.playSample(self.samplesSimilar[i])

    def play(self):
        self.playSample(self.currentSample)

    def play2(self):
        self.playSample(self.dropdownVar.get())

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

    def playSample(self, file):
        thread = Thread(target=lambda f=file: winsound.PlaySound(f, winsound.SND_FILENAME), args=(file,))
        thread.start()

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