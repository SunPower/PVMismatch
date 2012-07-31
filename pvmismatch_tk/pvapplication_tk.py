# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from PIL import Image, ImageTk
from Tkinter import Entry, StringVar, Frame, Label, Scale, Button, Toplevel, \
    IntVar, OptionMenu, Message, Spinbox, HORIZONTAL, LEFT, TOP, BOTH
from pvmodule_tk import PVmodule_tk
from pvstring_tk import PVstring_tk
from pvsystem_tk import PVsystem_tk
import os
MODULE_SIZES = [72, 96, 128]
MAX_STRINGS = 100
MAX_MODULES = 20

SPLOGO = os.path.join('res', 'logo_bg.png')
PVAPP_TXT = 'PVmismatch'
PVMODULE_TEXT = 'PVmodule'
PVSTRING_TEXT = 'PVstring'
PVSYSTEM_TEXT = 'PVsystem'


class PVapplicaton(Frame):
    """
    classdocs
    """

    def __init__(self, master=None):
        """
        Constructor
        """
        Frame.__init__(self, master)
        master.title(PVAPP_TXT)  # set title bar
        # if user resizes, expand frame and fill both sides
        self.pack(side=TOP, expand=True, fill=BOTH)

        # SP logo
        # set black background, pad sides with 15 points, top/bottom 5 points
        self.config(bg='black', padx='15', pady='5')
        self.SPlogo_png = Image.open(SPLOGO)  # create image object
        # convert image to tk-compatible format
        self.SPlogo = ImageTk.PhotoImage(self.SPlogo_png)
        self.SPlogoLbl = Label(self, image=self.SPlogo, borderwidth='0')
        self.SPlogoLbl.pack(side=TOP)
        # Intro text
        introtext = 'PVmismatch calculates I-V and P-V curves as well as the'
        introtext += '  max power point (MPP) for any sized system.'
        self.introMsg = Message(self, text=introtext, bg='black', fg='white')
        self.introMsg.pack(side=TOP, fill=BOTH)

        # separator
        self.separatorLine()

        # PVsystem Frame
        pvsysframe = self.PVsystemFrame = Frame(master)
        pvsysframe.pack(side=TOP, fill=BOTH)
        # number of strings integer variable
        numStr = self.numberStrings = IntVar(self)
        numStr.set(10)  # default
        # number of strings scale (slider)
        scaleCnf = {'from_': 1, 'to': MAX_STRINGS, 'orient': HORIZONTAL,
                     'variable': numStr, 'label': 'Number of Strings',
                     'length': '100'}
        self.PVsystemScale = Scale(pvsysframe, cnf=scaleCnf)
        self.PVsystemScale.pack(side=LEFT)
        # PVsystem button
        self.PVsystemButton = Button(pvsysframe, cnf={'text': PVSYSTEM_TEXT})
        self.PVsystemButton.pack(side=LEFT)
        self.PVsystemButton['command'] = self.startPVsystem_tk

        # separator
        self.separatorLine()

        # PVstring Frame
        pvstrframe = self.PVstringFrame = Frame(master)
        pvstrframe.pack(side=TOP, fill=BOTH)
        # number of modules integer variable
        numMod = self.numberModules = IntVar(self)
        numMod.set(10)  # default
        # number of strings scale (slider)
        scaleCnf = {'from_': 1, 'to': MAX_MODULES, 'orient': HORIZONTAL,
                     'variable': numMod, 'label': 'Number of Modules',
                     'length': '20'}
        self.PVstringScale = Scale(pvstrframe, cnf=scaleCnf)
        self.PVstringScale.pack(side=LEFT)
        # module ID # integer variable
        modID = self.moduleID = IntVar(self)
        modID.set(1)
        # module ID # spinbox
        self.modIDLabel = Label(pvstrframe, text='Module ID #')
        self.modIDLabel.pack(side=LEFT)
        spinboxCnf = {'from_': 1, 'to': 10,
                      'textvariable': str(modID)}
        self.modIDspinbox = Spinbox(pvstrframe, cnf=spinboxCnf)
        self.modIDspinbox.pack(side=LEFT)
        # PVmodule button
        self.PVstringButton = Button(pvstrframe, cnf={'text': PVSTRING_TEXT})
        self.PVstringButton.pack(side=LEFT)
        self.PVstringButton['command'] = self.startPVstring_tk

        # separator
        self.separatorLine()

        ## PVmodule
        pvmodframe = self.PVmoduleFrame = Frame(master)
        pvmodframe.pack(side=TOP, fill=BOTH)
        self.numberCells = IntVar(self)  # bind numberCells
        self.numberCells.set(MODULE_SIZES[0])  # default value
        self.numberCellsOption = OptionMenu(pvmodframe, self.numberCells,
                                            *MODULE_SIZES)
        self.numberCellsOption.pack(side=LEFT)
        self.cellIDlabel = Label(pvmodframe, text='Cell ID #')
        self.cellIDlabel.pack(side=LEFT)
        cellID = self.cellID = StringVar(self)  # bind moduleID
        self.cellID.set(1)
        spinboxCnf = {'from_': 1, 'to': 72,
                      'textvariable': str(cellID)}
        self.cellIDspinbox = Spinbox(pvmodframe, cnf=spinboxCnf)
        self.cellIDspinbox.pack(side=LEFT)
        self.PVmoduleButton = Button(pvmodframe,
                                     cnf={'text': PVMODULE_TEXT})
        self.PVmoduleButton.pack(side=LEFT)
        self.PVmoduleButton['command'] = self.startPVmodule_tk

        # separator
        self.separatorLine()

        # toolbar
        toolbar = self.toolbarframe = Frame(master)
        toolbar.pack(side=TOP, fill=BOTH)
        self.RESET = Button(toolbar, cnf={'text': 'Reset',
                                          'command': self.reset})
        self.RESET.pack({'side': 'left', 'fill': BOTH})
        self.LOAD = Button(toolbar, cnf={'text': 'Load', 'command': self.load})
        self.LOAD.pack({'side': 'left', 'fill': BOTH})
        self.SAVE = Button(toolbar, cnf={'text': 'Save', 'command': self.save})
        self.SAVE.pack({'side': 'left', 'fill': BOTH})
        self.QUIT = Button(toolbar, cnf={'text': 'Quit', 'command': self.quit})
        self.QUIT.pack({'side': 'left', 'fill': BOTH})

    def reset(self):
        print 'reset'

    def load(self):
        print 'load *.pv file'

    def save(self):
        print 'save *.pv file'

    def startPVmodule_tk(self):
        top = Toplevel()
        app = PVmodule_tk(self, top)
        app.mainloop()
        # please destroy me or I'll continue to run in background
        top.destroy()

    def startPVstring_tk(self):
        top = Toplevel()
        app = PVstring_tk(self, top)
        app.mainloop()
        # please destroy me or I'll continue to run in background
        top.destroy()

    def startPVsystem_tk(self):
        top = Toplevel()
        app = PVsystem_tk(self, top)
        app.mainloop()
        # please destroy me or I'll continue to run in background
        top.destroy()

    def separatorLine(self):
        sepCnf = {'height': '2', 'bg': 'white'}
        Frame(self.master, cnf=sepCnf).pack(side=TOP, fill=BOTH)
