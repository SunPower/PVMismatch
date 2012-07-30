# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from Tkinter import *
import os

SPLOGO = os.path.join('..', 'res', 'logo.png')
PVMODULE_TEXT = 'PVmodule'
PVSTRING_TEXT = 'PVstring'
PVSYSTEM_TEXT = 'PVsystem'
ROOT = Tk()


class PVapplicaton(Frame):
    """
    classdocs
    """

    def __init__(self, master=ROOT):
        """
        Constructor
        """
        Frame.__init__(self, master=None)
        self.pack()

        self['bg'] = 'black'
        self.SPlogo = BitmapImage(SPLOGO, cnf={''}, master)
        self.PVmoduleButton = Button(self, cnf={'text': PVMODULE_TEXT})
        self.PVstringButton = Button(self, cnf={'text': PVSTRING_TEXT})
        self.PVsystemButton = Button(self, cnf={'text': PVSYSTEM_TEXT})
        self.QUIT = Button(self, cnf={'text': 'Quit', 'command': self.quit})
