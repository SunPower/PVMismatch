# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""

from Tkinter import Frame, Label, Button, OptionMenu, IntVar, Menu, Entry
MODULE_SIZES = [72, 96, 128]


class PVmodule_tk(Frame):
    """
    classdocs
    """

    def __init__(self, pvapp, top):
        """
        Constructor
        """
        self.pvapp = pvapp
        Frame.__init__(self, top)
        self.pack(expand=True)  # if user resizes, expand Frame
        self.pack(fill='both')
        self.focus_set()  # get the focus
        self.grab_set()  # make this window modal

        self['bg'] = 'black'  # set black background
        self['padx'] = '15'  # pad sides with 15 points
        self['pady'] = '5'  # pad top/bottom 5 points
        self.master.title('PVmodule')  # set title bar
        self.SPlogoLabel = Label(self, image=self.pvapp.SPlogo,
                                 cnf={'borderwidth': '0'})
        self.SPlogoLabel.pack({'side': 'top'})

        self.numberCells = IntVar(self)  # bind numberCells
        self.numberCells.set(MODULE_SIZES[0])  # default value
        self.numberCellsOption = OptionMenu(self, self.numberCells,
                                            *MODULE_SIZES)
        self.numberCellsOption.pack({'side': 'top', 'fill': 'both'})

        self.QUIT = Button(self, cnf={'text': 'Quit', 'command': self.quit})
        self.QUIT.pack({'side': 'top', 'fill': 'both'})
