# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from PIL import Image, ImageTk
from Tkinter import Frame, Label, Scale, Button, Toplevel, IntVar, OptionMenu
from Tkinter import Entry, StringVar
from pvmodule_tk import PVmodule_tk
from pvstring_tk import PVstring_tk
from pvsystem_tk import PVsystem_tk
import os
MODULE_SIZES = [72, 96, 128]


SPLOGO = os.path.join('res', 'logo_bg.png')
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
        self.pack(expand=True)  # if user resizes, expand Frame
        self.pack(fill='both')  # if user resizes, fill both sides

        # SP logo
        self['bg'] = 'black'  # set black background
        self['padx'] = '15'  # pad sides with 15 points
        self['pady'] = '5'  # pad top/bottom 5 points
        self.master.title('PVmismatch')  # set title bar
        self.image = Image.open(SPLOGO)  # create image object
        # convert image to tk-compatible format
        self.SPlogo = ImageTk.PhotoImage(self.image)
        self.SPlogoLabel = Label(self, image=self.SPlogo,
                                 cnf={'borderwidth': '0'})
        self.SPlogoLabel.pack()  # side='top' is default
        # separator
        Frame(self, cnf={'height': '2', 'bg': 'white'}).pack(fill='both')

        # PVsystem Frame
        self.PVsystemFrame = Frame(self).pack(fill='both')
        self.PVsystemScale = Scale(self.PVsystemFrame)
        self.PVsystemScale.pack(side='left')
        self.PVsystemButton = Button(self.PVsystemFrame, cnf={'text': PVSYSTEM_TEXT})
        self.PVsystemButton.pack({'side': 'left'})
        self.PVsystemButton['command'] = self.startPVsystem_tk
        Frame(self, cnf={'height': '2', 'bg': 'white'}).pack(fill='both')

        # PVstring
        self.PVstringFrame = Frame(self).pack()
        self.PVstringButton = Button(self.PVstringFrame, cnf={'text': PVSTRING_TEXT})
        self.PVstringButton.pack({'side': 'top', 'fill': 'both'})
        self.PVstringButton['command'] = self.startPVstring_tk

        ## PVmodule
        self.PVmoduleFrame = Frame(self).pack(fill='both')
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
