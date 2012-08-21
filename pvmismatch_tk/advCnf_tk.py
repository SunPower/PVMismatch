# -*- coding: utf-8 -*-
"""
Created on Aug 18, 2012

@author: mmikofski
"""

from Tkconstants import W, E, RIGHT
from Tkinter import Frame, Label, Button, IntVar, Entry
import pvmismatch.pvconstants as pvconst
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
        top.title(PVAPP_TXT)  # set title bar
        top.protocol("WM_DELETE_WINDOW", self.quit)  # close window to quit
        CAPTION_FONT = tkFont.nametofont('TkCaptionFont')  # font for titles

        # variables
        Rs = self.Rs = IntVar(self, name='Rs')
        Rsh = self.Rsh = IntVar(self, name='Rsh')
        Isat1 = self.Isat1 = IntVar(self, name='Isat1')
        Isat2 = self.Isat2 = IntVar(self, name='Isat2')
        self.Rs.set("{:10.4e}".format(pvconst._Rs))  # IGNORE:W0212
        self.Rsh.set("{:10.4f}".format(pvconst._Rsh))  # IGNORE:W0212
        self.Isat1.set("{:10.4e}".format(pvconst._Isat1))  # IGNORE:W0212
        self.Isat2.set("{:10.4e}".format(pvconst._Isat2))  # IGNORE:W0212
        Aph = self.Aph = IntVar(self, name='Aph')
        Isc0 = self.Isc0 = IntVar(self, name='Isc0')
        T = self.T = IntVar(self, name='T')
        Vbypass = self.Vbypass = IntVar(self, name='Vbypasss')
        self.Aph.set("{:10.4e}".format(pvconst._Aph))  # IGNORE:W0212
        self.Isc0.set("{:10.4f}".format(pvconst._Isc0))  # IGNORE:W0212
        self.T.set("{:10.4f}".format(pvconst._T))  # IGNORE:W0212
        self.Vbypass.set("{:10.4f}".format(pvconst._Vbypass))  # IGNORE:W0212
        aRBD = self.aRBD = IntVar(self, name='aRBD')
        VRBD = self.VRBD = IntVar(self, name='VRBD')
        nRBD = self.nRBD = IntVar(self, name='nRBD')
        cellArea = self.cellArea = IntVar(self, name='cellArea')
        self.aRBD.set("{:10.4e}".format(pvconst._aRBD))  # IGNORE:W0212
        self.VRBD.set("{:10.4f}".format(pvconst._VRBD))  # IGNORE:W0212
        self.nRBD.set("{:10.4f}".format(pvconst._nRBD))  # IGNORE:W0212
        self.cellArea.set("{:10.4f}".format(pvconst._cellArea))  # IGNORE:W0212

        # layout
        _row = 0
        Label(self,
              text='Advanced Configuration',
              font=CAPTION_FONT).grid(row=_row, columnspan=3, sticky=W)
        _row += 1
        # Rs, Rsh, Isat1, Isat2
        Label(self, text='Rs [Ohms]').grid(row=_row, sticky=W)
        Label(self, text='Rsh [Ohms]').grid(row=(_row + 1), sticky=W)
        Label(self, text='Isat1 [A]').grid(row=(_row + 2), sticky=W)
        Label(self, text='Isat2 [A]').grid(row=(_row + 3), sticky=W)
        RsEntry = Entry(self, textvariable=Rs, width=15, justify=RIGHT)
        RsEntry.grid(row=_row, column=1)
        RshEntry = Entry(self, textvariable=Rsh, width=15, justify=RIGHT)
        RshEntry.grid(row=(_row + 1), column=1)
        Isat1Entry = Entry(self, textvariable=Isat1, width=15, justify=RIGHT)
        Isat1Entry.grid(row=(_row + 2), column=1)
        Isat2Entry = Entry(self, textvariable=Isat2, width=15, justify=RIGHT)
        Isat2Entry.grid(row=(_row + 3), column=1)
        _row += 4  # row 2, 3, 4, 5
        # Aph, Isc0, T, Vbypasss
        Label(self, text='Aph').grid(row=_row, sticky=W)
        Label(self, text='Isc0 [A]').grid(row=(_row + 1), sticky=W)
        Label(self, text='T [K]').grid(row=(_row + 2), sticky=W)
        Label(self, text='Vbypass [V]').grid(row=(_row + 3), sticky=W)
        RsEntry = Entry(self, textvariable=Aph, width=15, justify=RIGHT)
        RsEntry.grid(row=_row, column=1)
        RshEntry = Entry(self, textvariable=Isc0, width=15, justify=RIGHT)
        RshEntry.grid(row=(_row + 1), column=1)
        Isat1Entry = Entry(self, textvariable=T, width=15, justify=RIGHT)
        Isat1Entry.grid(row=(_row + 2), column=1)
        Isat2Entry = Entry(self, textvariable=Vbypass, width=15, justify=RIGHT)
        Isat2Entry.grid(row=(_row + 3), column=1)
        _row += 4
        # aRBD, VRBD, nRBD, cellArea
        Label(self, text='aRBD').grid(row=_row, sticky=W)
        Label(self, text='VRBD [V]').grid(row=(_row + 1), sticky=W)
        Label(self, text='nRBD').grid(row=(_row + 2), sticky=W)
        Label(self, text='cell area [cm^2]').grid(row=(_row + 3), sticky=W)
        RsEntry = Entry(self, textvariable=aRBD, width=15, justify=RIGHT)
        RsEntry.grid(row=_row, column=1)
        RshEntry = Entry(self, textvariable=VRBD, width=15, justify=RIGHT)
        RshEntry.grid(row=(_row + 1), column=1)
        Isat1Entry = Entry(self, textvariable=nRBD, width=15, justify=RIGHT)
        Isat1Entry.grid(row=(_row + 2), column=1)
        Isat2Entry = Entry(self,
                           textvariable=cellArea, width=15, justify=RIGHT)
        Isat2Entry.grid(row=(_row + 3), column=1)
        _row += 4
        Button(self, text='OK',
               command=self.okay).grid(row=_row, sticky=(E + W))
        Button(self, text='Cancel',
               command=self.quit).grid(row=_row, column=1, sticky=(E + W))

    def okay(self):
        self.quit()
