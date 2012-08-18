# -*- coding: utf-8 -*-
"""
Created on Aug 18, 2012

@author: mmikofski
"""

from Tkconstants import W, E
from Tkinter import Frame, Label, Button, IntVar, Entry
#from pvmismatch_tk.pvapplication_tk import PVAPP_TXT
import tkFont

PVAPP_TXT = 'PVmismatch'


class AdvCnf_tk(Frame):
    """
    classdocs
    """

    def __init__(self, pvapp, top):
        """
        Constructor
        """
        self.pvapp = pvapp
        Frame.__init__(self, top)
        self.pack()
        self.focus_set()  # get the focus
        self.grab_set()  # make this window modal
        top.resizable(False, False)  # not resizable in x or y
        top.title(PVAPP_TXT)  # set title bar of master (a.k.a. root)
        top.protocol("WM_DELETE_WINDOW", self.quit)  # close window to quit
        CAPTION_FONT = tkFont.nametofont('TkCaptionFont')  # font for titles
        # number of strings integer variable
        Rs = self.Rs = IntVar(self, 1, 'Rs')
        # number of strings integer variable
        self.Rs.set(1)  # default
        _row = 0
        Label(self,
              text='Advanced Configuration',
              font=CAPTION_FONT).grid(row=_row, columnspan=3, sticky=W)
        # Rs, Rsh, Isat1, Isat2
        _row += 1  # row 2, 3, 4, 5
        Label(self, text='Rs [Ohms]').grid(row=_row)
        Label(self, text='Rsh [Ohms]').grid(row=(_row + 1))
        Label(self, text='Isat1 [A]').grid(row=(_row + 2))
        Label(self, text='Isat2 [A]').grid(row=(_row + 3))
        RsEntry = Entry(self, textvariable=Rs)
        RsEntry.grid(row=_row, column=1)
        RshEntry = Entry(self, text=1)
        RshEntry.grid(row=(_row + 1), column=1)
        Isat1Entry = Entry(self, text=1)
        Isat1Entry.grid(row=(_row + 2), column=1)
        Isat2Entry = Entry(self, text=1)
        Isat2Entry.grid(row=(_row + 3), column=1)
        _row += 4
        Button(self, text='OK',
               command=self.okay).grid(row=_row, sticky=(E + W))
        Button(self, text='Cancel',
               command=self.quit).grid(row=_row, column=1, sticky=(E + W))

    def okay(self):
        self.quit()
