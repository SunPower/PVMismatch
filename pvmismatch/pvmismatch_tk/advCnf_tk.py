# -*- coding: utf-8 -*-
"""
Created on Aug 18, 2012

@author: mmikofski
"""

from Tkconstants import W, E, RIGHT
from Tkinter import Frame, Label, Button, DoubleVar, Entry, IntVar
import tkFont

PVAPP_TXT = 'PVmismatch'
INTEGERS = '0123456789'
FLOATS = '.' + INTEGERS


class AdvCnf_tk(Frame):
    """
    classdocs
    """

    def __init__(self, pvapp, top):
        """
        Constructor
        """
        self.pvapp = pvapp
        Frame.__init__(self, top, name='advCnf')
        self.pack()
        self.focus_set()  # get the focus
        self.grab_set()  # make this window modal
        top.resizable(False, False)  # not resizable in x or y
        top.title(PVAPP_TXT)  # set title bar
        top.protocol("WM_DELETE_WINDOW", self.quit)  # close window to quit
        CAPTION_FONT = tkFont.nametofont('TkCaptionFont')  # font for titles

        # variables
        cellnum = self.cellnum = IntVar(self, name='cellnum')
        Rs = self.Rs = DoubleVar(self, name='Rs')
        Rsh = self.Rsh = DoubleVar(self, name='Rsh')
        Isat1_T0 = self.Isat1_T0 = DoubleVar(self, name='Isat1_T0')
        Isat2 = self.Isat2 = DoubleVar(self, name='Isat2')
        Rs.set("{:10.4e}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].pvcells[cellnum.get() % pvapp.numCells.get()].Rs))
        Rsh.set("{:10.4f}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].pvcells[cellnum.get() % pvapp.numCells.get()].Rsh))
        Isat1_T0.set("{:10.4e}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].pvcells[cellnum.get() % pvapp.numCells.get()].Isat1_T0))
        Isat2.set("{:10.4e}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].pvcells[cellnum.get() % pvapp.numCells.get()].Isat2))
        Aph = self.Aph = DoubleVar(self, name='Aph')
        Isc0_T0 = self.Isc0_T0 = DoubleVar(self, name='Isc0_T0')
        Tcell = self.Tcell = DoubleVar(self, name='Tcell')
        Vbypass = self.Vbypass = DoubleVar(self, name='Vbypasss')
        Aph.set("{:10.4f}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].pvcells[cellnum.get() % pvapp.numCells.get()].Aph))
        Isc0_T0.set("{:10.4f}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].pvcells[cellnum.get() % pvapp.numCells.get()].Isc0_T0))
        Tcell.set("{:10.4f}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].pvcells[cellnum.get() % pvapp.numCells.get()].Tcell))
        Vbypass.set("{:10.4f}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].Vbypass))
        aRBD = self.aRBD = DoubleVar(self, name='aRBD')
        VRBD = self.VRBD = DoubleVar(self, name='VRBD')
        nRBD = self.nRBD = DoubleVar(self, name='nRBD')
        cellArea = self.cellArea = DoubleVar(self, name='cellArea')
        aRBD.set("{:10.4e}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].pvcells[cellnum.get() % pvapp.numCells.get()].aRBD))
        VRBD.set("{:10.4f}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].pvcells[cellnum.get() % pvapp.numCells.get()].VRBD))
        nRBD.set("{:10.4f}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].pvcells[cellnum.get() % pvapp.numCells.get()].nRBD))
        cellArea.set("{:10.4f}".format(pvapp.pvSys.pvmods[cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].cellArea))

        # must register vcmd and invcmd as Tcl functions
        vcmd = (self.register(self.validateWidget),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        invcmd = (self.register(self.invalidWidget),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # layout
        _row = 0
        Label(self,
              text='Advanced Configuration',
              font=CAPTION_FONT).grid(row=_row, columnspan=3, sticky=W)
        _row += 1
        # cellnum, Rs, Rsh, Isat1_T0
        Label(self, text='cell #').grid(row=_row, sticky=W)
        Label(self, text='Rs [Ohms]').grid(row=_row + 1, sticky=W)
        Label(self, text='Rsh [Ohms]').grid(row=(_row + 2), sticky=W)
        Label(self, text='Isat1_T0 [A]').grid(row=(_row + 3), sticky=W)
        cellnumEntry = Entry(self, textvariable=cellnum, width=12, justify=RIGHT,
                             name='cellnumEntry', validatecommand=vcmd,
                             invalidcommand=invcmd, validate='all')
        cellnumEntry.grid(row=_row, column=1)
        RsEntry = Entry(self, textvariable=Rs, width=12, justify=RIGHT,
                        name='rsEntry', validatecommand=vcmd,
                        invalidcommand=invcmd, validate='all')
        RsEntry.grid(row=_row + 1, column=1)
        RshEntry = Entry(self, textvariable=Rsh, width=12, justify=RIGHT,
                         name='rshEntry', validatecommand=vcmd,
                         invalidcommand=invcmd, validate='all')
        RshEntry.grid(row=(_row + 2), column=1)
        Isat1_T0Entry = Entry(self, textvariable=Isat1_T0, width=12,
                              justify=RIGHT, name='isat1_T0Entry',
                              validatecommand=vcmd, invalidcommand=invcmd,
                              validate='all')
        Isat1_T0Entry.grid(row=(_row + 3), column=1)
        _row += 4  # row 2, 3, 4, 5
        # Isat2, Isc0_T0, Tcell, Vbypasss
        Label(self, text='Isat2 [A]').grid(row=(_row), sticky=W)
        Label(self, text='Isc0_T0 [A]').grid(row=(_row + 1), sticky=W)
        Label(self, text='Tcell [K]').grid(row=(_row + 2), sticky=W)
        Label(self, text='Vbypass [V]').grid(row=(_row + 3), sticky=W)
        Isat2Entry = Entry(self, textvariable=Isat2, width=12, justify=RIGHT,
                           name='isat2Entry', validatecommand=vcmd,
                           invalidcommand=invcmd, validate='all')
        Isat2Entry.grid(row=(_row), column=1)
        Isc01_T0Entry = Entry(self, textvariable=Isc0_T0, width=12,
                             justify=RIGHT, name='isc01_T0Entry',
                             validatecommand=vcmd, invalidcommand=invcmd,
                             validate='all')
        Isc01_T0Entry.grid(row=(_row + 1), column=1)
        TcellEntry = Entry(self, textvariable=Tcell, width=12, justify=RIGHT,
                           name='tcellEntry', validatecommand=vcmd,
                           invalidcommand=invcmd, validate='all')
        TcellEntry.grid(row=(_row + 2), column=1)
        VbypassEntry = Entry(self, textvariable=Vbypass, width=12,
                             justify=RIGHT, name='vbypassEntry',
                             validatecommand=vcmd, invalidcommand=invcmd,
                             validate='all')
        VbypassEntry.grid(row=(_row + 3), column=1)
        _row += 4
        # aRBD, VRBD, nRBD, cellArea
        Label(self, text='aRBD').grid(row=_row, sticky=W)
        Label(self, text='VRBD [V]').grid(row=(_row + 1), sticky=W)
        Label(self, text='nRBD').grid(row=(_row + 2), sticky=W)
        Label(self, text='cell area [cm^2]').grid(row=(_row + 3), sticky=W)
        aRBDEntry = Entry(self, textvariable=aRBD, width=12, justify=RIGHT,
                          name='aRBDEntry', validatecommand=vcmd,
                          invalidcommand=invcmd, validate='all')
        aRBDEntry.grid(row=_row, column=1)
        VRBDEntry = Entry(self, textvariable=VRBD, width=12, justify=RIGHT,
                          name='vRBDEntry', validatecommand=vcmd,
                          invalidcommand=invcmd, validate='all')
        VRBDEntry.grid(row=(_row + 1), column=1)
        nRBDEntry = Entry(self, textvariable=nRBD, width=12, justify=RIGHT,
                          name='nRBDEntry', validatecommand=vcmd,
                          invalidcommand=invcmd, validate='all')
        nRBDEntry.grid(row=(_row + 2), column=1)
        cellAreaEntry = Entry(self, textvariable=cellArea, width=12,
                              justify=RIGHT, name='cellAreaEntry',
                              validatecommand=vcmd, invalidcommand=invcmd,
                              validate='all')
        cellAreaEntry.grid(row=(_row + 3), column=1)
        _row += 4
        Button(self, text='OK',
               command=self.okay).grid(row=_row, sticky=(E + W))
        Button(self, text='Cancel',
               command=self.quit).grid(row=_row, column=1, sticky=(E + W))

    def okay(self):
        # get the new values
        validationConstants = self.pvapp.validationConstants
        messagetext = self.pvapp.messagetext
        Rs = self.Rs.get()
        if not (0 < Rs <= validationConstants["advCnf"]["Rs"]):
            self.pvapp.msgtext.set('Invalid series resistance!')
            self.bell()
            return
        Rsh = self.Rsh.get()
        if not (0 < Rsh <= validationConstants["advCnf"]["Rsh"]):
            self.pvapp.msgtext.set('Invalid shunt resistance!')
            self.bell()
            return
        Isat1_T0 = self.Isat1_T0.get()
        if not 0 < Isat1_T0 <= validationConstants["advCnf"]["Isat1_T0"]:
            self.pvapp.msgtext.set('Invalid diode-1 saturation current!')
            self.bell()
            return
        Isat2 = self.Isat2.get()
        if not 0 < Isat2 <= validationConstants["advCnf"]["Isat2"]:
            self.pvapp.msgtext.set('Invalid diode-2 saturation current!')
            self.bell()
            return
        Aph = self.Aph.get()
        if not 0 < Aph <= validationConstants["advCnf"]["Aph"]:
            errtext = 'Invalid photo-generated current coefficient!'
            self.pvapp.msgtext.set(errtext)
            self.bell()
            return
        Isc0_T0 = self.Isc0_T0.get()
        if not 1 < Isc0_T0 <= validationConstants["advCnf"]["Isc0_T0"]:
            self.pvapp.msgtext.set('Invalid short circuit current!')
            self.bell()
            return
        Tcell = self.Tcell.get()
        if not 0 < Tcell <= validationConstants["advCnf"]["Tcell"]:
            self.pvapp.msgtext.set('Invalid cell temperature!')
            self.bell()
            return
        cellArea = self.cellArea.get()
        if not 0 < cellArea <= validationConstants["advCnf"]["cellArea"]:
            self.pvapp.msgtext.set('Invalid cell area!')
            self.bell()
            return
        Vbypass = self.Vbypass.get()
        if not 0 > Vbypass >= validationConstants["advCnf"]["Vbypass"]:
            errtext = 'Invalid bypass diode trigger voltage!'
            self.pvapp.msgtext.set(errtext)
            self.bell()
            return
        aRBD = self.aRBD.get()
        if not 0 < aRBD <= validationConstants["advCnf"]["aRBD"]:
            errtext = 'Invalid reverse bias breakdown coefficient (aRBD)!'
            self.pvapp.msgtext.set(errtext)
            self.bell()
            return
        VRBD = self.VRBD.get()
        if not 0 > VRBD >= validationConstants["advCnf"]["VRBD"]:
            errtext = 'Invalid reverse bias breakdown voltage!'
            self.pvapp.msgtext.set(errtext)
            self.bell()
            return
        nRBD = self.nRBD.get()
        if not 0 < nRBD <= validationConstants["advCnf"]["nRBD"]:
            errtext = 'Invalid reverse bias breakdown exponent (nRBD)!'
            self.pvapp.msgtext.set(errtext)
            self.bell()
            return
        # update PVconstants
        self.pvapp.msgtext.set(messagetext["pvapplication"]["Ready"])
        pvapp = self.pvapp
        kwargs = {'Rs': Rs, 'Rsh': Rsh, 'Isat1_T0': Isat1_T0, 'Isat2': Isat2, 'Isc0_T0': Isc0_T0, 'Tcell': Tcell, 'aRBD': aRBD, 'VRBD': VRBD, 'nRBD': nRBD}
        pvapp.pvSys.pvmods[self.cellnum.get() / (pvapp.numCells.get() * pvapp.numMods.get())][(self.cellnum.get() / pvapp.numCells.get()) % pvapp.numMods.get()].pvcells[self.cellnum.get() % pvapp.numCells.get()].update(
            **kwargs
        )  # cellArea, Vbypass updated by module
        # update PVapplication_tk
        self.pvapp.updatePVsys(pvapp.pvSys)
        self.pvapp.updateIVstats()
        self.quit()

#    Validation substitutions
#    %d  Type of action: 1 for insert, 0 for delete, or -1 for focus, forced or
#        textvariable validation.
#    %i  Index of char string to be inserted/deleted, if any, otherwise -1.
#    %P  The value of the spinbox should edition occur. If you are configuring
#        the spinbox widget to have a new textvariable, this will be the value
#        of that textvariable.
#    %s  The current value of spinbox before edition.
#    %S  The text string being inserted/deleted, if any. Otherwise it is an
#        empty string.
#    %v  The type of validation currently set.
#    %V  The type of validation that triggered the callback (key, focusin,
#        focusout, forced).
#    %W  The name of the spinbox widget.

# TODO: Fix these functions so that delete and overwrite work

    def validateWidget(self, *args):
        # W = Tkinter.W = 'w' is already used, so use W_ instead
        (d, i, P, s, S, v, V, W_) = args  # @UnusedVariable # IGNORE:W0612
        print "OnValidate:",
        print("d={}, i={}, P={}, s={}, S={}, v={}, V={}, W={}".format(*args))
        if W_ == '.advCnfTop.advCnf.rsEntry':
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.rshEntry':
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.isat1_T0Entry':
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.isat2Entry':
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.aphEntry':
            valType = FLOATS
            valTest = lambda val: float(val) - 1  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.isc01_T0Entry':
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.tcellEntry':
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.vbypassEntry':
            valType = FLOATS
            valTest = lambda val: -float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.aRBDEntry':
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.vRBDEntry':
            valType = FLOATS
            valTest = lambda val: -float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.nRBDEntry':
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.cellAreaEntry':
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.cellnumEntry':
            valType = INTEGERS
            valTest = lambda val: int(val)  # IGNORE:W0108
        else:
            return False
        w = self.nametowidget(W_)
        w.config(validate=v)
        if S in valType:
            try:
                valTest(P)
            except ValueError:
                return False
            return True
        else:
            return False

    def invalidWidget(self, *args):
        (d, i, P, s, S, v, V, W_) = args  # @UnusedVariable # IGNORE:W0612
        print "OnInvalid: ",
        print("d={}, i={}, P={}, s={}, S={}, v={}, V={}, W={}".format(*args))
        if W_ == ".advCnfTop.advCnf.rsEntry":
            errText = 'Invalid series resistance!'
        elif W_ == ".advCnfTop.advCnf.rshEntry":
            errText = 'Invalid shunt resistance!'
        elif W_ == ".advCnfTop.advCnf.isat1_T0Entry":
            errText = 'Invalid diode-1 saturation current!'
        elif W_ == ".advCnfTop.advCnf.isat2Entry":
            errText = 'Invalid diode-2 saturation current!'
        elif W_ == ".advCnfTop.advCnf.aphEntry":
            errText = 'Invalid photo-generated current coefficient!'
        elif W_ == ".advCnfTop.advCnf.isc01_T0Entry":
            errText = 'Invalid short circuit current!'
        elif W_ == ".advCnfTop.advCnf.tcellEntry":
            errText = 'Invalid cell temperature!'
        elif W_ == ".advCnfTop.advCnf.vbypassEntry":
            errText = 'Invalid bypass diode trigger voltage!'
        elif W_ == ".advCnfTop.advCnf.aRBDEntry":
            errText = 'Invalid reverse bias breakdown coefficient (aRBD)!'
        elif W_ == ".advCnfTop.advCnf.vRBDEntry":
            errText = 'Invalid reverse bias breakdown voltage!'
        elif W_ == ".advCnfTop.advCnf.nRBDEntry":
            errText = 'Invalid reverse bias breakdown exponent (nRBD)!'
        elif W_ == ".advCnfTop.advCnf.cellAreaEntry":
            errText = 'Invalid cell area!'
        elif W_ == ".advCnfTop.advCnf.cellnumEntry":
            errText = 'Invalid cell number!'
        else:
            errText = 'Unknown widget!'
        w = self.nametowidget(W_)
        w.config(validate=v)
        self.pvapp.msgtext.set(errText)
        self.bell()
