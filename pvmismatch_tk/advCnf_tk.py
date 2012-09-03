# -*- coding: utf-8 -*-
"""
Created on Aug 18, 2012

@author: mmikofski
"""

from Tkconstants import W, E, RIGHT
from Tkinter import Frame, Label, Button, DoubleVar, Entry
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
        Tcell = self.Tcell = DoubleVar(self, name='Tcell')
        Vbypass = self.Vbypass = DoubleVar(self, name='Vbypasss')
        Aph.set("{:10.4f}".format(pvapp.pvSys.pvconst.Aph))
        Isc0.set("{:10.4f}".format(pvapp.pvSys.pvconst.Isc0))
        Tcell.set("{:10.4f}".format(pvapp.pvSys.pvconst.Tcell))
        Vbypass.set("{:10.4f}".format(pvapp.pvSys.pvconst.Vbypass))
        aRBD = self.aRBD = DoubleVar(self, name='aRBD')
        VRBD = self.VRBD = DoubleVar(self, name='VRBD')
        nRBD = self.nRBD = DoubleVar(self, name='nRBD')
        cellArea = self.cellArea = DoubleVar(self, name='cellArea')
        aRBD.set("{:10.4e}".format(pvapp.pvSys.pvconst.aRBD))
        VRBD.set("{:10.4f}".format(pvapp.pvSys.pvconst.VRBD))
        nRBD.set("{:10.4f}".format(pvapp.pvSys.pvconst.nRBD))
        cellArea.set("{:10.4f}".format(pvapp.pvSys.pvconst.cellArea))

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
        # Rs, Rsh, Isat1, Isat2
        Label(self, text='Rs [Ohms]').grid(row=_row, sticky=W)
        Label(self, text='Rsh [Ohms]').grid(row=(_row + 1), sticky=W)
        Label(self, text='Isat1 [A]').grid(row=(_row + 2), sticky=W)
        Label(self, text='Isat2 [A]').grid(row=(_row + 3), sticky=W)
        RsEntry = Entry(self, textvariable=Rs, width=12, justify=RIGHT,
                        name='rsEntry', validatecommand=vcmd,
                        invalidcommand=invcmd, validate='all')
        RsEntry.grid(row=_row, column=1)
        RshEntry = Entry(self, textvariable=Rsh, width=12, justify=RIGHT,
                         name='rshEntry', validatecommand=vcmd,
                         invalidcommand=invcmd, validate='all')
        RshEntry.grid(row=(_row + 1), column=1)
        Isat1Entry = Entry(self, textvariable=Isat1, width=12, justify=RIGHT,
                           name='isat1Entry', validatecommand=vcmd,
                           invalidcommand=invcmd, validate='all')
        Isat1Entry.grid(row=(_row + 2), column=1)
        Isat2Entry = Entry(self, textvariable=Isat2, width=12, justify=RIGHT,
                           name='isat2Entry', validatecommand=vcmd,
                           invalidcommand=invcmd, validate='all')
        Isat2Entry.grid(row=(_row + 3), column=1)
        _row += 4  # row 2, 3, 4, 5
        # Aph, Isc0, Tcell, Vbypasss
        Label(self, text='Aph').grid(row=_row, sticky=W)
        Label(self, text='Isc0 [A]').grid(row=(_row + 1), sticky=W)
        Label(self, text='Tcell [K]').grid(row=(_row + 2), sticky=W)
        Label(self, text='Vbypass [V]').grid(row=(_row + 3), sticky=W)
        AphEntry = Entry(self, textvariable=Aph, width=12, justify=RIGHT,
                         name='aphEntry', validatecommand=vcmd,
                         invalidcommand=invcmd, validate='all')
        AphEntry.grid(row=_row, column=1)
        Isc0Entry = Entry(self, textvariable=Isc0, width=12, justify=RIGHT,
                         name='isc0Entry', validatecommand=vcmd,
                         invalidcommand=invcmd, validate='all')
        Isc0Entry.grid(row=(_row + 1), column=1)
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
        Rs = self.Rs.get()
        Rsh = self.Rsh.get()
        Isat1 = self.Isat1.get()
        Isat2 = self.Isat2.get()
        Aph = self.Aph.get()
        Isc0 = self.Isc0.get()
        Tcell = self.Tcell.get()
        cellArea = self.cellArea.get()
        Vbypass = self.Vbypass.get()
        aRBD = self.aRBD.get()
        VRBD = self.VRBD.get()
        nRBD = self.nRBD.get()
        # update PVconstants
        pvapp = self.pvapp
        pvapp.pvSys.pvconst.update(Rs, Rsh, Isat1, Isat2, Aph, Isc0, Tcell,
                                   cellArea, Vbypass, aRBD, VRBD, nRBD)
        # update PVapplication_tk
        self.pvapp.updatePVsys()
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
            maxVal = 1
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.rshEntry':
            maxVal = 100
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.isat1Entry':
            maxVal = 1
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.isat2Entry':
            maxVal = 1
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.aphEntry':
            maxVal = 10
            valType = FLOATS
            valTest = lambda val: float(val) - 1  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.isc0Entry':
            maxVal = 100
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.tcellEntry':
            maxVal = 500
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.vbypassEntry':
            maxVal = 1
            valType = FLOATS
            valTest = lambda val: -float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.aRBDEntry':
            maxVal = 1
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.vRBDEntry':
            maxVal = 50
            valType = FLOATS
            valTest = lambda val: -float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.nRBDEntry':
            maxVal = 10
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        elif W_ == '.advCnfTop.advCnf.cellAreaEntry':
            maxVal = 200
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
        else:
            return False
        w = self.nametowidget(W_)
        w.config(validate=v)
        if S in valType:
            try:
                val = valTest(P)
            except ValueError:
                return False
            return 0 < val <= maxVal
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
        elif W_ == ".advCnfTop.advCnf.isat1Entry":
            errText = 'Invalid diode-1 saturation current!'
        elif W_ == ".advCnfTop.advCnf.isat2Entry":
            errText = 'Invalid diode-2 saturation current!'
        elif W_ == ".advCnfTop.advCnf.aphEntry":
            errText = 'Invalid photo-generated current coefficient!'
        elif W_ == ".advCnfTop.advCnf.isc0Entry":
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
        else:
            errText = 'Unknown widget!'
        w = self.nametowidget(W_)
        w.config(validate=v)
        self.pvapp.msgtext.set(errText)
        self.bell()
