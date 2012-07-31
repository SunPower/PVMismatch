# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from PIL import Image, ImageTk
from Tkinter import StringVar, Frame, Label, Scale, Button, Toplevel, IntVar, \
    OptionMenu, Message, Spinbox, HORIZONTAL, LEFT, BOTH, W
from pvmodule_tk import PVmodule_tk
from pvstring_tk import PVstring_tk
from pvsystem_tk import PVsystem_tk
import os

MOD_SIZES = [72, 96, 128]
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
        Frame.__init__(self, master, name='pvapp')
        master.resizable(True, False)  # only resize width
        master.title(PVAPP_TXT)  # set title bar of master (a.k.a. root)
        # set black background, pad sides with 15 points, top/bottom 5 points
        self.config(bg='black', padx='5', pady='5')
        # fill=BOTH fills in padding with background color
        # w/o fill=BOTH padding is default color
        # side=TOP is the default
        self.pack(fill=BOTH)

        # SP logo
        self.SPlogo_png = Image.open(SPLOGO)  # create image object
        # convert image to tk-compatible format (.gif, .pgm, or .ppm)
        self.SPlogo = ImageTk.PhotoImage(self.SPlogo_png)
        # bg='black' fills extra space with black
        # anchor=W aligns photoimage on left side, NW is no different
        # padding is ignored by images, use borderwidth
        self.SPlogoLabel = Label(self, name='spLogoLabel', image=self.SPlogo,
                                 borderwidth='5', anchor=W, bg='black')
        # fill=BOTH expands the photoimage to fill parent frame
        # w/o fill=BOTH photoimage is centered in frame even with anchor=W
        self.SPlogoLabel.pack(fill=BOTH)
        # Intro text
        introtext = 'PVmismatch calculates I-V and P-V curves as well as the'
        introtext += '  max power point (MPP) for any sized system.'
        # anchor=W aligns message on left side, NW is no different
        # fg='white' sets text color to white, default is black, so it doesn't
        #   show on black background
        # default aspect is 150%, about as wide as high, or set width>0
        self.introMsg = Message(self, name='introMsg', text=introtext,
                                anchor=W, bg='black', fg='white', width='2000')
        # fill=BOTH expands the message to fill parent frame
        # w/o fill=BOTH message is centered in frame even with anchor=W
        self.introMsg.pack(fill=BOTH)

        # PVsystem frame
        pvsysframe = self.PVsystemFrame = Frame(master, name='')
        pvsysframe.pack(fill=BOTH)
        # number of strings integer variable
        numStr = self.numberStrings = IntVar(self)
        numStr.set(10)  # default
        # number of strings scale (slider)
        scaleCnf = {'from_': 1, 'to': MAX_STRINGS, 'orient': HORIZONTAL,
                     'variable': numStr, 'label': 'Number of Strings',
                     'length': '500'}
        self.PVsystemScale = Scale(pvsysframe, cnf=scaleCnf)
        self.PVsystemScale.pack(side=LEFT)
        # PVsystem button
        self.PVsystemButton = Button(pvsysframe, cnf={'text': PVSYSTEM_TEXT})
        self.PVsystemButton.pack(side=LEFT)
        self.PVsystemButton['command'] = self.startPVsystem_tk

        self.separatorLine()  # separator

        # PVstring frame
        pvstrframe = self.PVstringFrame = Frame(master)
        pvstrframe.pack(fill=BOTH)
        # number of modules integer variable
        numMod = self.numberModules = IntVar(self)
        numMod.set(10)  # default
        # number of strings scale (slider)
        scaleCnf = {'from_': 1, 'to': MAX_MODULES, 'orient': HORIZONTAL,
                     'variable': numMod, 'label': 'Number of Modules',
                     'length': '100'}
        self.PVstringScale = Scale(pvstrframe, cnf=scaleCnf)
        self.PVstringScale.pack(side=LEFT)
        # module ID # integer variable
        modID = self.moduleID = IntVar(self)
        modID.set(1)
        # module ID # label
        self.modIDLabel = Label(pvstrframe, text='Module ID #')
        self.modIDLabel.pack(side=LEFT)
        # module ID # spinbox
        spinboxCnf = {'from_': 1, 'to': 10,
                      'textvariable': str(modID)}
        self.modIDspinbox = Spinbox(pvstrframe, cnf=spinboxCnf)
        self.modIDspinbox.pack(side=LEFT)
        # PVmodule button
        self.PVstringButton = Button(pvstrframe, cnf={'text': PVSTRING_TEXT})
        self.PVstringButton.pack(side=LEFT)
        self.PVstringButton['command'] = self.startPVstring_tk

        self.separatorLine()  # separator

        ## PVmodule frame
        pvmodframe = self.PVmoduleFrame = Frame(master)
        pvmodframe.pack(fill=BOTH)
        # number of cells integer variable
        numCells = self.numberCells = IntVar(self)  # bind numberCells
        numCells.set(MOD_SIZES[0])  # default value
        # number of cells option menu
        self.numberCellsOption = OptionMenu(pvmodframe, numCells, *MOD_SIZES)
        self.numberCellsOption.pack(side=LEFT)
        # cell ID # label
        self.cellIDlabel = Label(pvmodframe, text='Cell ID #')
        self.cellIDlabel.pack(side=LEFT)
        # cell ID # spinbox
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

        self.separatorLine()  # separator

        # toolbar
        toolbar = self.toolbarframe = Frame(master)
        toolbar.pack(fill=BOTH)
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
        # master is known in constructor, but not here!
        Frame(self.master, height='2', bg='white').pack(fill=BOTH)
