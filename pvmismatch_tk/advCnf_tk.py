# -*- coding: utf-8 -*-
"""
Created on Aug 18, 2012

@author: mmikofski
"""

from Tkconstants import W, E, RIGHT
from Tkinter import Frame, Label, Button, DoubleVar, Entry
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
        Rs = self.Rs = DoubleVar(self, name='Rs')
        Rsh = self.Rsh = DoubleVar(self, name='Rsh')
        Isat1 = self.Isat1 = DoubleVar(self, name='Isat1')
        Isat2 = self.Isat2 = DoubleVar(self, name='Isat2')
        Rs.set("{:10.4e}".format(pvapp.pvSys.pvconst.Rs))
        Rsh.set("{:10.4f}".format(pvapp.pvSys.pvconst.Rsh))
        Isat1.set("{:10.4e}".format(pvapp.pvSys.pvconst.Isat1))
        Isat2.set("{:10.4e}".format(pvapp.pvSys.pvconst.Isat2))
        Aph = self.Aph = DoubleVar(self, name='Aph')
        Isc0 = self.Isc0 = DoubleVar(self, name='Isc0')
        T = self.T = DoubleVar(self, name='T')
        Vbypass = self.Vbypass = DoubleVar(self, name='Vbypasss')
        Aph.set("{:10.4e}".format(pvapp.pvSys.pvconst.Aph))
        Isc0.set("{:10.4f}".format(pvapp.pvSys.pvconst.Isc0))
        T.set("{:10.4f}".format(pvapp.pvSys.pvconst.T))
        Vbypass.set("{:10.4f}".format(pvapp.pvSys.pvconst.Vbypass))
        aRBD = self.aRBD = DoubleVar(self, name='aRBD')
        VRBD = self.VRBD = DoubleVar(self, name='VRBD')
        nRBD = self.nRBD = DoubleVar(self, name='nRBD')
        cellArea = self.cellArea = DoubleVar(self, name='cellArea')
        aRBD.set("{:10.4e}".format(pvapp.pvSys.pvconst.aRBD))
        VRBD.set("{:10.4f}".format(pvapp.pvSys.pvconst.VRBD))
        nRBD.set("{:10.4f}".format(pvapp.pvSys.pvconst.nRBD))
        cellArea.set("{:10.4f}".format(pvapp.pvSys.pvconst.cellArea))

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
        RsEntry = Entry(self, textvariable=Rs, width=12, justify=RIGHT)
        RsEntry.grid(row=_row, column=1)
        RshEntry = Entry(self, textvariable=Rsh, width=12, justify=RIGHT)
        RshEntry.grid(row=(_row + 1), column=1)
        Isat1Entry = Entry(self, textvariable=Isat1, width=12, justify=RIGHT)
        Isat1Entry.grid(row=(_row + 2), column=1)
        Isat2Entry = Entry(self, textvariable=Isat2, width=12, justify=RIGHT)
        Isat2Entry.grid(row=(_row + 3), column=1)
        _row += 4  # row 2, 3, 4, 5
        # Aph, Isc0, T, Vbypasss
        Label(self, text='Aph').grid(row=_row, sticky=W)
        Label(self, text='Isc0 [A]').grid(row=(_row + 1), sticky=W)
        Label(self, text='T [K]').grid(row=(_row + 2), sticky=W)
        Label(self, text='Vbypass [V]').grid(row=(_row + 3), sticky=W)
        RsEntry = Entry(self, textvariable=Aph, width=12, justify=RIGHT)
        RsEntry.grid(row=_row, column=1)
        RshEntry = Entry(self, textvariable=Isc0, width=12, justify=RIGHT)
        RshEntry.grid(row=(_row + 1), column=1)
        Isat1Entry = Entry(self, textvariable=T, width=12, justify=RIGHT)
        Isat1Entry.grid(row=(_row + 2), column=1)
        Isat2Entry = Entry(self, textvariable=Vbypass, width=12, justify=RIGHT)
        Isat2Entry.grid(row=(_row + 3), column=1)
        _row += 4
        # aRBD, VRBD, nRBD, cellArea
        Label(self, text='aRBD').grid(row=_row, sticky=W)
        Label(self, text='VRBD [V]').grid(row=(_row + 1), sticky=W)
        Label(self, text='nRBD').grid(row=(_row + 2), sticky=W)
        Label(self, text='cell area [cm^2]').grid(row=(_row + 3), sticky=W)
        RsEntry = Entry(self, textvariable=aRBD, width=12, justify=RIGHT)
        RsEntry.grid(row=_row, column=1)
        RshEntry = Entry(self, textvariable=VRBD, width=12, justify=RIGHT)
        RshEntry.grid(row=(_row + 1), column=1)
        Isat1Entry = Entry(self, textvariable=nRBD, width=12, justify=RIGHT)
        Isat1Entry.grid(row=(_row + 2), column=1)
        Isat2Entry = Entry(self,
                           textvariable=cellArea, width=12, justify=RIGHT)
        Isat2Entry.grid(row=(_row + 3), column=1)
        _row += 4
        Button(self, text='OK',
               command=self.okay).grid(row=_row, sticky=(E + W))
        Button(self, text='Cancel',
               command=self.quit).grid(row=_row, column=1, sticky=(E + W))

    def okay(self):
        # get the new values
        Rs = self.Rs.get()
        Rsh = self.Rsh.get()
        Isat1 = self.Isat1.get()
        Isat2 = self.Isat2.get()
        Aph = self.Aph.get()
        Isc0 = self.Isc0.get()
        T = self.T.get()
        cellArea = self.cellArea.get()
        Vbypass = self.Vbypass.get()
        aRBD = self.aRBD.get()
        VRBD = self.VRBD.get()
        nRBD = self.nRBD.get()
        # update PVconstants
        self.pvapp.pvSys.pvconst.update(Rs, Rsh, Isat1, Isat2, Aph, Isc0, T,
                                        cellArea, Vbypass, aRBD, VRBD, nRBD)
        # update PVapplication_tk
        self.pvapp.updatePVsys()
        self.pvapp.updateIVstats()
        self.quit()
