# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from PIL import Image, ImageTk
from Tkinter import Entry, StringVar, Frame, Label, Scale, Button, Toplevel, \
    IntVar, OptionMenu, Message, Spinbox, HORIZONTAL, LEFT
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
        master = self.master  # create a shortcut to the top level
        master.title(PVAPP_TXT)  # set title bar
        # if user resizes, expand frame and fill both sides
        self.pack(side='top', expand=True, fill='both')

        # SP logo
        self.config(bg='black', padx='15', pady='5')
#        self['bg'] = 'black'  # set black background
#        self['padx'] = '15'  # pad sides with 15 points
#        self['pady'] = '5'  # pad top/bottom 5 points
        self.SPlogo_png = Image.open(SPLOGO)  # create image object
        # convert image to tk-compatible format
        self.SPlogo = ImageTk.PhotoImage(self.SPlogo_png)
        Label(self, image=self.SPlogo, borderwidth='0').pack(side=LEFT)
        # Intro text
        introtext = 'PVmismatch calculates I-V and P-V curves as well as the'
        introtext += '  max power point (MPP) for any sized system.'
        Message(self, text=introtext, bg='black').pack(fill='both')

        # separator
        Frame(master, cnf={'height': '2', 'bg': 'white'}).pack(fill='both')

        # PVsystem Frame
        pvsysframe = self.PVsystemFrame = Frame(master).pack(fill='both')
        # number of strings integer variable
        numStr = self.numberStrings = IntVar(self)
        numStr.set(10)  # default
        # number of strings scale (slider)
        scaleCnf = {'from_': 1, 'to': MAX_STRINGS, 'orient': HORIZONTAL,
                     'variable': numStr, 'label': 'Number of Strings',
                     'length': '100'}
        self.PVsystemScale = Scale(pvsysframe, cnf=scaleCnf).pack(side=LEFT)
        # PVsystem button
        self.PVsystemButton = Button(pvsysframe, cnf={'text': PVSYSTEM_TEXT})
        self.PVsystemButton.pack(side=LEFT)
        self.PVsystemButton['command'] = self.startPVsystem_tk

        # separator
        Frame(master, cnf={'height': '2', 'bg': 'white'}).pack(fill='both')

        # PVstring Frame
        pvstrframe = self.PVstringFrame = Frame(master).pack(fill='both')
        # number of modules integer variable
        numMod = self.numberModules = IntVar(self)
        numMod.set(10)  # default
        # number of strings scale (slider)
        scaleCnf = {'from_': 1, 'to': MAX_MODULES, 'orient': HORIZONTAL,
                     'variable': numMod, 'label': 'Number of Modules',
                     'length': '20'}
        self.PVstringScale = Scale(pvstrframe, cnf=scaleCnf).pack(side=LEFT)
        # module ID # integer variable
        modID = self.moduleID = IntVar(self)
        modID.set(1)
        # module ID # spinbox
        Label(pvstrframe,text='Module ID #').pack(side=LEFT)
        spinboxCnf = {'from_': 1, 'to': 10,
                      'textvariable': str(modID)}
        self.PVstringSpinBox = Spinbox(pvstrframe, cnf=spinboxCnf)
        self.PVstringSpinBox.pack(side=LEFT)
        # PVmodule button
        self.PVstringButton = Button(pvstrframe, cnf={'text': PVSTRING_TEXT})
        self.PVstringButton.pack(side=LEFT)
        self.PVstringButton['command'] = self.startPVstring_tk

        # separator
        Frame(master, cnf={'height': '2', 'bg': 'white'}).pack(fill='both')

        ## PVmodule
        pvmodframe = self.PVmoduleFrame = Frame(master).pack(fill='both')
        self.numberCells = IntVar(self)  # bind numberCells
        self.numberCells.set(MODULE_SIZES[0])  # default value
        self.numberCellsOption = OptionMenu(pvmodframe, self.numberCells,
                                            *MODULE_SIZES)
        self.numberCellsOption.pack({'side': LEFT})
        self.moduleIDlabel = Label(pvmodframe,
                                   cnf={'text': 'Module ID'})
        self.moduleIDlabel.pack(side=LEFT)
        self.moduleID = StringVar(self)  # bind moduleID
        self.moduleID.set(1)
        self.moduleIDentry = Entry(pvmodframe,
                                   textvariable=self.moduleID)
        self.moduleIDentry.insert(0, '1')
        self.moduleIDentry.pack(side=LEFT)
        self.PVmoduleButton = Button(pvmodframe,
                                     cnf={'text': PVMODULE_TEXT})
        self.PVmoduleButton.pack({'side': LEFT})
        self.PVmoduleButton['command'] = self.startPVmodule_tk
        Frame(self, cnf={'height': '2', 'bg': 'white'}).pack({'fill': 'both'})

        # separator
        Frame(master, cnf={'height': '2', 'bg': 'white'}).pack(fill='both')

        # toolbar
        toolbar = self.toolbarframe = Frame(master).pack(fill='both')
        self.RESET = Button(toolbar, cnf={'text': 'Reset',
                                          'command': self.reset})
        self.RESET.pack({'side': 'left', 'fill': 'both'})
        self.LOAD = Button(toolbar, cnf={'text': 'Load', 'command': self.load})
        self.LOAD.pack({'side': 'left', 'fill': 'both'})
        self.SAVE = Button(toolbar, cnf={'text': 'Save', 'command': self.save})
        self.SAVE.pack({'side': 'left', 'fill': 'both'})
        self.QUIT = Button(toolbar, cnf={'text': 'Quit', 'command': self.quit})
        self.QUIT.pack({'side': 'left', 'fill': 'both'})

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
