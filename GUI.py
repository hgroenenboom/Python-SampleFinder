from tkinter import Tk, Label, Button, StringVar, OptionMenu
import subprocess
import os
import winsound

class MyGUI:
    currentSample = ""
    samplesSimilar = [ "swag", "lol" ]

    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.label = Label(master, text="This is our first GUI!")
        self.label.pack()

        self.greet_button = Button(master, text="set new samples")
        self.greet_button.pack()

        self.w = Label(master, text=" ... ")
        self.w.pack()
        self.play_button = Button(master, text="Play", command=self.play)
        self.play_button.pack()


        self.dropdownVar = StringVar()
        self.dropdownVar.set(self.samplesSimilar[0])
        self.popupMenu = OptionMenu(master, self.dropdownVar, *self.samplesSimilar)
        self.popmenLabel = Label(master, text="Choose similar sample")
        self.popmenLabel.pack()
        self.popupMenu.pack()
        # self.dropdownVar.trace('w', self.change_dropdown)

        self.play_button2 = Button(master, text="Play", command=self.play2)
        self.play_button2.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

    def play(self):
        self.playSample(self.currentSample)

    def play2(self):
        self.playSample(self.dropdownVar.get())

    def change_dropdown(self, *args):
        print(self.dropdownVar.get())

    def playSample(self, file):
        winsound.PlaySound(file, winsound.SND_FILENAME)

root = Tk()
my_gui = MyGUI(root)