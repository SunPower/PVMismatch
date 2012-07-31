# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from PIL import Image, ImageTk
from Tkinter import Entry, StringVar, Frame, Label, Scale, Button, Toplevel, \
    IntVar, OptionMenu, Message, HORIZONTAL, Spinbox
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
        self.pack({'expand': True, 'fill': 'both'})

        # SP logo
        self.config(bg='black', padx='15', pady='5')
#        self['bg'] = 'black'  # set black background
#        self['padx'] = '15'  # pad sides with 15 points
#        self['pady'] = '5'  # pad top/bottom 5 points
        self.SPlogo_png = Image.open(SPLOGO)  # create image object
        # convert image to tk-compatible format
        self.SPlogo = ImageTk.PhotoImage(self.SPlogo_png)
        Label(self, image=self.SPlogo, borderwidth='0').pack(side='left')
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
        self.PVsystemScale = Scale(pvsysframe, cnf=scaleCnf).pack(side='left')
        # PVsystem button
        self.PVsystemButton = Button(pvsysframe, cnf={'text': PVSYSTEM_TEXT})
        self.PVsystemButton.pack(side='left')
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
        self.PVstringScale = Scale(pvstrframe, cnf=scaleCnf).pack(side='left')
        # module ID # integer variable
        modID = self.moduleID = IntVar(self)
        modID.set(1)
        # module ID # spinbox
        spinboxCnf = {'from_': 1, 'to': numStr, 'variable': modID,
                      'label': 'Module ID #'}
        self.PVstringSpinBox = Spinbox(pvstrframe, cnf=spinboxCnf)
        self.PVstringSpinBox.pack(side='left')
        # PVmodule button
        self.PVstringButton = Button(pvstrframe, cnf={'text': PVSTRING_TEXT})
        self.PVstringButton.pack(side=top')
        self.PVstringButton['command'] = self.startPVstring_tk

        # separator
        Frame(master, cnf={'height': '2', 'bg': 'white'}).pack(fill='both')

        ## PVmodule
        self.PVmoduleFrame = Frame(master).pack(fill='both')
        self.numberCells = IntVar(self)  # bind numberCells
        self.numberCells.set(MODULE_SIZES[0])  # default value
        self.numberCellsOption = OptionMenu(self.PVmoduleFrame, self.numberCells,
                                            *MODULE_SIZES)
        self.numberCellsOption.pack({'side': 'left'})
        self.moduleIDlabel = Label(self.PVmoduleFrame,
                                   cnf={'text': 'Module ID'})
        self.moduleIDlabel.pack(side='left')
        self.moduleID = StringVar(self)  # bind moduleID
        self.moduleID.set(1)
        self.moduleIDentry = Entry(self.PVmoduleFrame,
                                   textvariable=self.moduleID)
        self.moduleIDentry.insert(0, '1')
        self.moduleIDentry.pack(side='left')
        self.PVmoduleButton = Button(self.PVmoduleFrame,
                                     cnf={'text': PVMODULE_TEXT})
        self.PVmoduleButton.pack({'side': 'left'})
        self.PVmoduleButton['command'] = self.startPVmodule_tk
        Frame(self, cnf={'height': '2', 'bg': 'white'}).pack({'fill': 'both'})

        self.QUIT = Button(self, cnf={'text': 'Quit', 'command': self.quit})
        self.QUIT.pack({'side': 'top', 'fill': 'both'})

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
