# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from PIL import Image, ImageTk
from Tkinter import Frame, Label, Button, Toplevel, OptionMenu, Scale, Entry, \
    Message, Spinbox, IntVar, StringVar, RIGHT, LEFT, BOTH, E, W, HORIZONTAL
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2TkAgg
from numpy import interp, squeeze
from pvmismatch.pvmodule import PTS, NPTS
from pvmismatch.pvsystem import PVsystem
from pvmismatch_tk.pvstring_tk import PVstring_tk
import os
import tkFont

INTEGERS = '0123456789'
MOD_SIZES = [72, 96, 128]
MAX_STRINGS = 100
MAX_MODULES = 20
SPLOGO = os.path.join('res', 'logo_bg.png')
PVAPP_TXT = 'PVmismatch'
READY_MSG = 'Ready'


class PVapplicaton(Frame):
    """
    classdocs
    """

    def __init__(self, master=None):
        """
        Constructor
        """
        Frame.__init__(self, master)
        master.resizable(False, False)  # not resizable in x or y
        master.title(PVAPP_TXT)  # set title bar of master (a.k.a. root)
        master.protocol("WM_DELETE_WINDOW", self._quit)  # close window to quit
        CAPTION_FONT = tkFont.nametofont('TkCaptionFont')  # font for titles

        # number of strings integer variable
        numStrs = self.numStrs = IntVar(self, 10, 'numStrs')
        # number of modules integer variable
        numMods = self.numMods = IntVar(self, 10, 'numMods')
        # number of cells integer variable
        numCells = self.numCells = IntVar(self, MOD_SIZES[1], 'numCells')
        # text representations of I-V Characteristics
        txtIsys = self.txtIsys = StringVar(self, name='txtIsys')
        txtVsys = self.txtVsys = StringVar(self, name='txtVsys')
        txtPsys = self.txtPsys = StringVar(self, name='txtPsys')
        txtImp = self.txtImp = StringVar(self, name='txtImp')
        txtVmp = self.txtVmp = StringVar(self, name='txtVmp')
        txtPmp = self.txtPmp = StringVar(self, name='txtPmp')
        txtIsc = self.txtIsc = StringVar(self, name='txtIsc')
        txtVoc = self.txtVoc = StringVar(self, name='txtVoc')
        txtFF = self.txtFF = StringVar(self, name='txtFF')
        txtEff = self.txteff = StringVar(self, name='txtEff')

        # PVsystem
        pvSys = self.pvSys = PVsystem()
        # TODO: run in asynchronous thread, add progress meter
        (Imp, Vmp, Pmp, Isc, Voc, FF, eff) = pvSys.calcMPP_IscVocFFeff()
        txtImp.set("{:7.3f}".format(Imp))  # [A]
        txtVmp.set("{:7.3f}".format(Vmp))  # [V]
        txtPmp.set("{:7.3f}".format(Pmp / 1000))  # [kW] convert to kW
        txtIsc.set("{:7.3f}".format(Isc))  # [A]
        txtVoc.set("{:7.3f}".format(Voc))  # [V]
        txtFF.set("{:7.3f}".format(FF * 100))  # [%] convert to %
        txtEff.set("{:7.3f}".format(eff * 100))  # [%] convert to %

        # must register vcmd and invcmd as Tcl functions
        vcmd = (self.register(self.validateWidget),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        invcmd = (self.register(self.invalidWidget),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # SP logo
        self._name = 'pvApplication'  # set name of frame widget
        # set black background, pad sides with 15 points, top/bottom 5 points
        self.config(bg='black', padx=5, pady=5)
        # fill=BOTH fills in padding with background color
        # w/o fill=BOTH padding is default color
        # side=TOP is the default
        self.pack(fill=BOTH)
        # convert image to tk-compatible format (.gif, .pgm, or .ppm)
        self.SPlogo = ImageTk.PhotoImage(Image.open(SPLOGO))
        # bg='black' fills extra space with black
        # anchor=W aligns photoimage on left side, NW is no different
        # padding is ignored by images, use borderwidth
        Label(self, image=self.SPlogo, borderwidth=5, bg='black',
              anchor=W).pack(fill=BOTH)
        # fill=BOTH expands the photoimage to fill parent frame
        # w/o fill=BOTH photoimage is centered in frame even with anchor=W
        # Intro text
        introText = 'PVmismatch calculates I-V and P-V curves as well as the'
        introText += ' max power point (MPP) for any sized system.\nSet the'
        introText += ' number of strings in the system, the number of modules'
        introText += ' per string and the number cells per module.'
        # anchor=W aligns message on left side, NW is no different
        # fg='white' sets text color to white, default is black, so it doesn't
        #   show on black background
        # default aspect is 150%, about as wide as high, or set width>0
        Message(self, text=introText, width=750, bg='black', fg='white',
                anchor=W).pack(fill=BOTH)
        # fill=BOTH expands the message to fill parent frame
        # w/o fill=BOTH message is centered in frame even with anchor=W

        # PVsystem frame
        pvSysFrame = self.pvSysFrame = Frame(master, name='pvSysFrame')
        # fill=BOTH keeps widgets in frame on left when window is resized
        pvSysFrame.pack(fill=BOTH)

        # PVsystem matplotlib figure canvas
        self.pvSysPlotFrame = Frame(pvSysFrame, name='pvSysPlotFrame')
        pvSysPlotFrame = self.pvSysPlotFrame
        pvSysPlotFrame.pack(side=RIGHT)
        pvSysPlot = self.pvSysPlot = pvSys.plotSys()
        self.pvSysFigCanvas = FigureCanvasTkAgg(pvSysPlot,
                                                master=pvSysPlotFrame,
                                                resize_callback=None)
        pvSysFigCanvas = self.pvSysFigCanvas
        pvSysFigCanvas.get_tk_widget()._name = 'pvSysFigCanvas'  # IGNORE:W0212
        pvSysFigCanvas.show()
        # NB: FigureCanvasTkAgg._tkcanvas is FigureCanvasTkAgg.get_tk_widget()
        pvSysFigCanvas.get_tk_widget().pack(fill=BOTH)
        pvSysToolbar = NavigationToolbar2TkAgg(pvSysFigCanvas, pvSysPlotFrame)
        pvSysToolbar.update()
        pvSysToolbar.pack(fill=BOTH)

        # PVsystem data frame
        pvSysDataFrame = self.pvSysDataFrame = Frame(pvSysFrame,
                                                     name='pvSysDataFrame')
        pvSysDataFrame.pack(side=LEFT)
        _row = 0
        Label(pvSysDataFrame,
              text='PVsystem', font=CAPTION_FONT).grid(row=_row, columnspan=3,
                                                     sticky=W)

        # number of strings label
        _row += 1  # row 1
        Label(pvSysDataFrame,
              text='Number of Strings').grid(row=_row, columnspan=2, sticky=W)
        # number of strings spinbox
        # use textVar to set number of strings from LOAD, RESET or default
        spinboxCnf = {'name': 'numStrSpinbox', 'from_': 1, 'to': MAX_STRINGS,
                      'textvariable': numStrs, 'width': 5, 'validate': 'all',
                      'validatecommand': vcmd, 'invalidcommand': invcmd}
        self.numStrSpinbox = Spinbox(pvSysDataFrame, cnf=spinboxCnf)
        self.numStrSpinbox.grid(row=_row, column=2)

        # number of modules label
        _row += 1  # row 2
        Label(pvSysDataFrame,
              text='Number of Modules').grid(row=_row, columnspan=2, sticky=W)
        # number of modules spinbox
        spinboxCnf = {'name': 'numModSpinbox', 'from_': 1, 'to': MAX_MODULES,
                      'textvariable': numMods, 'width': 5, 'validate': 'all',
                      'validatecommand': vcmd, 'invalidcommand': invcmd}
        self.numModSpinbox = Spinbox(pvSysDataFrame, cnf=spinboxCnf)
        self.numModSpinbox.grid(row=_row, column=2)

        # number of cells label
        _row += 1  # row 3
        Label(pvSysDataFrame,
              text='Number of Cells').grid(row=_row, columnspan=2, sticky=W)
        # number of cells option menu
        # http://www.logilab.org/card/pylintfeatures#basic-checker
        # pylint: disable = W0142
        self.numCellOption = OptionMenu(pvSysDataFrame, numCells, *MOD_SIZES)
        # pylint: enable = W0142
        self.numCellOption._name = 'numCellOption'  # IGNORE:W0212
        self.numCellOption.grid(row=_row, column=2)

        # Advanced Configuration button
        _row += 1  # row 14
        buttonCnf = {'name': 'advCnfButton', 'text': 'Advanced Configuration',
                     'command': self.startAdvCnf_tk}
        pvStrButton = self.pvStrButton = Button(pvSysDataFrame, buttonCnf)
        pvStrButton.grid(row=_row, columnspan=3, sticky=(E + W))

        # slider to explore IV curves
        _row += 1  # row 4, 5 & 6
#        _getIV = self.register(self.getIV)
        self.pvSysScale = Scale(pvSysDataFrame, orient=HORIZONTAL,
                                label='I-V Curve', font=CAPTION_FONT,
                                command=self.getIV, showvalue=False,
                                from_=0, to=(NPTS - 1))
        self.pvSysScale.grid(row=_row, columnspan=3, sticky=(E + W))
        # Isys
        Label(pvSysDataFrame, text='Isys [A]').grid(row=(_row + 1))
        self.pvIsys = Entry(pvSysDataFrame, textvariable=txtIsys,
                            width=7)
        self.pvIsys.grid(row=(_row + 2))
        # Vsys
        Label(pvSysDataFrame, text='Vsys [V]').grid(row=(_row + 1), column=1)
        self.pvVsys = Entry(pvSysDataFrame, textvariable=txtVsys,
                            width=7)
        self.pvVsys.grid(row=(_row + 2), column=1)
        # Psys
        Label(pvSysDataFrame, text='Psys [kW]').grid(row=(_row + 1), column=2)
        self.pvPsys = Entry(pvSysDataFrame, textvariable=txtPsys,
                            width=7)
        self.pvPsys.grid(row=(_row + 2), column=2)

        # Imp, Vmp & Pmp
        _row += 3  # row 7, 8, 9, 10, 11 & 12
        Label(pvSysDataFrame,
              text='I-V Characteristics',
              font=CAPTION_FONT).grid(row=_row, columnspan=3, sticky=W)
        Label(pvSysDataFrame, text='Imp [A]').grid(row=(_row + 1))
        Label(pvSysDataFrame, text='Vmp [V]').grid(row=(_row + 1), column=1)
        Label(pvSysDataFrame, text='Pmp [kW]').grid(row=(_row + 1), column=2)
        self.pvImp = Entry(pvSysDataFrame, textvariable=txtImp,
                            width=7, state='readonly')
        self.pvImp.grid(row=(_row + 2))
        self.pvVmp = Entry(pvSysDataFrame, textvariable=txtVmp,
                            width=7, state='readonly')
        self.pvVmp.grid(row=(_row + 2), column=1)
        self.pvPmp = Entry(pvSysDataFrame, textvariable=txtPmp,
                            width=7, state='readonly')
        self.pvPmp.grid(row=(_row + 2), column=2)
        # Isc, Voc & FF
        Label(pvSysDataFrame, text='Isc [A]').grid(row=(_row + 3))
        Label(pvSysDataFrame, text='Voc [V]').grid(row=(_row + 3), column=1)
        Label(pvSysDataFrame, text='FF [%]').grid(row=(_row + 3), column=2)
        self.pvIsc = Entry(pvSysDataFrame, textvariable=txtIsc,
                            width=7, state='readonly')
        self.pvIsc.grid(row=(_row + 4))
        self.pvVoc = Entry(pvSysDataFrame, textvariable=txtVoc,
                            width=7, state='readonly')
        self.pvVoc.grid(row=(_row + 4), column=1)
        self.pvFF = Entry(pvSysDataFrame, textvariable=txtFF,
                            width=7, state='readonly')
        self.pvFF.grid(row=(_row + 4), column=2)
        Label(pvSysDataFrame, text='Efficiency [%]').grid(row=(_row + 5),
                                                          columnspan=2)
        self.pvEff = Entry(pvSysDataFrame, textvariable=txtEff,
                            width=7, state='readonly')
        self.pvEff.grid(row=(_row + 5), column=2)

        # number of modules label
        _row += 6  # row 13
        Label(pvSysDataFrame, text='Irradiance [suns]',
              font=CAPTION_FONT).grid(row=_row, columnspan=2, sticky=W)
        # number of modules spinbox
        spinboxCnf = {'name': 'sunSpinbox', 'from_': 0.2, 'to': 10,
                       'increment': 0.1, 'width': 5}
        self.sunSpinbox = Spinbox(pvSysDataFrame, cnf=spinboxCnf)
        self.sunSpinbox.grid(row=_row, column=2)

        # PVstring button
        _row += 1  # row 14
        buttonCnf = {'name': 'pvStrButton', 'text': 'PVstring',
                     'command': self.startPVstring_tk}
        pvStrButton = self.pvStrButton = Button(pvSysDataFrame, buttonCnf)
        pvStrButton.grid(row=_row, columnspan=3, sticky=(E + W))

        # toolbar
        toolbar = self.toolbarframe = Frame(master, name='toolbar')
        toolbar.pack(fill=BOTH)
        self.QUIT = Button(toolbar, text='Quit', command=self._quit)
        self.QUIT.pack(side=RIGHT)
        self.SAVE = Button(toolbar, text='Save', command=self.save)
        self.SAVE.pack(side=RIGHT)
        self.LOAD = Button(toolbar, text='Load', command=self.load)
        self.LOAD.pack(side=RIGHT)
        self.RESET = Button(toolbar, text='Reset', command=self.reset)
        self.RESET.pack(side=RIGHT)
        self.MESSAGE = Message(toolbar, text=READY_MSG, width=150)
        self.MESSAGE.pack(side=LEFT)

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
        if W_ == ".pvSysFrame.pvSysDataFrame.numStrSpinbox":
            maxVal = MAX_STRINGS
        elif W_ == ".pvSysFrame.pvSysDataFrame.numModSpinbox":
            maxVal = MAX_MODULES
        else:
            pass
        w = self.nametowidget(W_)
        w.config(validate=v)
        if S in INTEGERS:
            try:
                intVar = int(P)
            except ValueError:
                return False
            return 0 < intVar <= maxVal
        else:
            return False

    def invalidWidget(self, *args):
        (d, i, P, s, S, v, V, W_) = args  # @UnusedVariable # IGNORE:W0612
        print "OnInvalid: ",
        print("d={}, i={}, P={}, s={}, S={}, v={}, V={}, W={}".format(*args))
        if W_ == ".pvSysFrame.pvSysDataFrame.numStrSpinbox":
            errText = 'Invalid number of strings!'
        elif W_ == ".pvSysFrame.pvSysDataFrame.numModSpinbox":
            errText = 'Invalid number of modules!'
        else:
            pass
        w = self.nametowidget(W_)
        w.config(validate=v)
        self.MESSAGE.config(fg='red', text=errText, width=150)
        self.bell()

    def getIV(self, *args):
        print args
        x = float(args[0]) / NPTS
        xp = squeeze(PTS)
        Vsys = interp(x, xp, self.pvSys.Vsys.squeeze())
        Isys = interp(x, xp, self.pvSys.Isys.squeeze())
        Psys = Vsys * Isys / 1000
        self.txtVsys.set("{:7.3f}".format(Vsys))
        self.txtIsys.set("{:7.3f}".format(Isys))
        self.txtPsys.set("{:7.3f}".format(Psys))

    def startPVstring_tk(self):
        top = Toplevel()
        app = PVstring_tk(self, top)
        app.mainloop()
        # please destroy me or I'll continue to run in background
        top.destroy()

    def startAdvCnf_tk(self):
        top = Toplevel()
        CAPTION_FONT = tkFont.nametofont('TkCaptionFont')  # font for titles
        _row = 0
        Label(top,
              text='Advanced Configuration',
              font=CAPTION_FONT).grid(row=_row, columnspan=3, sticky=W)
        # Rs, Rsh, Isat1, Isat2
        _row += 1  # row 2, 3, 4, 5
        Label(top, text='Rs [Ohms]').grid(row=_row)
        Label(top, text='Rsh [Ohms]').grid(row=(_row + 1), column=1)
        Label(top, text='Isat1 [A]').grid(row=(_row + 2), column=2)
        Label(top, text='Isat2 [A]').grid(row=(_row + 3), column=2)
        Rs = Entry(top, text=1)
        Rs.grid(row=_row, column=1)
        Rsh = Entry(top, text=1)
        Rsh.grid(row=(_row + 1), column=1)
        Isat1 = Entry(top, text=1)
        Isat1.grid(row=(_row + 2), column=1)
        Isat2 = Entry(top, text=1)
        Isat2.grid(row=(_row + 3), column=1)
        top.mainloop()
        # please destroy me or I'll continue to run in background
        top.destroy()

    def reset(self):
        # number of strings integer variable
        self.numStrs.set(10)  # default
        # number of modules integer variable
        self.numMods.set(10)  # default
        # number of cells integer variable
        self.numCells.set(MOD_SIZES[1])  # default value is 96
        self.MESSAGE.config(fg='black', text=READY_MSG, width=150)
        print 'reset'

    def load(self):
        print 'load *.pv file'

    def save(self):
        print 'save *.pv file'

    def _quit(self):
        # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        self.master.quit()  # stops mainloop
        self.master.destroy()
