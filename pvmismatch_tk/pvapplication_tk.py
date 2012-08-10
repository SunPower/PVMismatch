# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from PIL import Image, ImageTk
from Tkinter import Frame, Label, Button, Toplevel, OptionMenu, Scale, Entry, \
    Message, Spinbox, IntVar, StringVar, RIGHT, LEFT, BOTH, E, W, HORIZONTAL
from pvmismatch_tk.pvmodule_tk import PVmodule_tk
from pvmismatch_tk.pvstring_tk import PVstring_tk
from pvmismatch_tk.pvsystem_tk import PVsystem_tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2TkAgg
from pvmismatch.pvsystem import PVsystem
from pvmismatch.pvmodule import PTS, NPTS
from numpy import interp, squeeze
import os

INTEGERS = '0123456789'
MOD_SIZES = [72, 96, 128]
MAX_STRINGS = 100
MAX_MODULES = 20
PVSYSTEMSCALE = 500
PVSTRINGSCALE = 500
SPLOGO = os.path.join('res', 'logo_bg.png')
PVAPP_TXT = 'PVmismatch'
PVMODULE_TEXT = 'PVmodule'
PVSTRING_TEXT = 'PVstring'
PVSYSTEM_TEXT = 'PVsystem'
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
        master.protocol("WM_DELETE_WINDOW", self._quit)

        # number of strings integer variable
        numStr = self.numberStrings = IntVar(self)
        numStr.set(10)  # default
        # number of modules integer variable
        numMod = self.numberModules = IntVar(self)
        numMod.set(10)  # default
        # number of cells integer variable
        numCells = self.numberCells = IntVar(self)  # bind numberCells
        numCells.set(MOD_SIZES[1])  # default value
        # number of strings integer variable
        strID = self.stringID = IntVar(self)
        strID.set(1)  # default
        # text representation of Isys
        txtIsys = self.txtIsys = StringVar(self)
        txtIsys.set(0)  # default
        # text representation of Vsys
        txtVsys = self.txtVsys = StringVar(self)
        txtVsys.set(0)  # default
        # text representation of Psys
        txtPsys = self.txtPsys = StringVar(self)
        txtPsys.set(0)  # default
        # text representation of Imp
        txtImp = self.txtImp = StringVar(self)
        txtImp.set(0)  # default
        # text representation of Vmp
        txtVmp = self.txtVmp = StringVar(self)
        txtVmp.set(0)  # default
        # text representation of Vmp
        txtPmp = self.txtPmp = StringVar(self)
        txtPmp.set(0)  # default
        # text representation of Isc
        txtIsc = self.txtIsc = StringVar(self)
        txtIsc.set(0)  # default
        # text representation of Voc
        txtVoc = self.txtVoc = StringVar(self)
        txtVoc.set(0)  # default
        # text representation of FF
        txtFF = self.txtFF = StringVar(self)
        txtFF.set(0)  # default

        # PVsystem
        pvSys = self.pvSys = PVsystem()

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
        self.SPlogo_png = Image.open(SPLOGO)  # create image object
        # convert image to tk-compatible format (.gif, .pgm, or .ppm)
        self.SPlogo = ImageTk.PhotoImage(self.SPlogo_png)
        # bg='black' fills extra space with black
        # anchor=W aligns photoimage on left side, NW is no different
        # padding is ignored by images, use borderwidth
        self.SPlogoLabel = Label(self, name='spLogoLabel', image=self.SPlogo,
                                 borderwidth=5, bg='black', anchor=W)
        # fill=BOTH expands the photoimage to fill parent frame
        # w/o fill=BOTH photoimage is centered in frame even with anchor=W
        self.SPlogoLabel.pack(fill=BOTH)
        # Intro text
        introText = 'PVmismatch calculates I-V and P-V curves as well as the'
        introText += '  max power point (MPP) for any sized system.'
        # anchor=W aligns message on left side, NW is no different
        # fg='white' sets text color to white, default is black, so it doesn't
        #   show on black background
        # default aspect is 150%, about as wide as high, or set width>0
        self.introMsg = Message(self, name='introMsg', text=introText,
                                width=1000, bg='black', fg='white', anchor=W)
        # fill=BOTH expands the message to fill parent frame
        # w/o fill=BOTH message is centered in frame even with anchor=W
        self.introMsg.pack(fill=BOTH)

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
        Label(pvSysDataFrame, text='PVsystem').grid(row=0, columnspan=3,
                                                    sticky=W)

        # number of strings label
        labelCnf = {'name': 'numStrLabel', 'text': 'Number of Strings'}
        self.numStrLabel = Label(pvSysDataFrame, cnf=labelCnf)
        self.numStrLabel.grid(row=1, columnspan=2, sticky=W)
        # number of strings spinbox
        # use textVar to set number of strings from LOAD, RESET or default
        spinboxCnf = {'name': 'numStrSpinbox', 'from_': 1, 'to': MAX_STRINGS,
                      'textvariable': numStr, 'width': 5, 'validate': 'all',
                      'validatecommand': vcmd, 'invalidcommand': invcmd}
        self.numStrSpinbox = Spinbox(pvSysDataFrame, cnf=spinboxCnf)
        self.numStrSpinbox.grid(row=1, column=2)

        # number of modules label
        labelCnf = {'name': 'numModLabel', 'text': 'Number of Modules'}
        self.numModLabel = Label(pvSysDataFrame, cnf=labelCnf)
        self.numModLabel.grid(row=2, columnspan=2, sticky=W)
        # number of modules spinbox
        spinboxCnf = {'name': 'numModSpinbox', 'from_': 1, 'to': MAX_MODULES,
                      'textvariable': numMod, 'width': 5, 'validate': 'all',
                      'validatecommand': vcmd, 'invalidcommand': invcmd}
        self.numModSpinbox = Spinbox(pvSysDataFrame, cnf=spinboxCnf)
        self.numModSpinbox.grid(row=2, column=2)

        # number of cells label
        labelCnf = {'name': 'numCellLabel', 'text': 'Number of Cells'}
        self.numCellLabel = Label(pvSysDataFrame, cnf=labelCnf)
        self.numCellLabel.grid(row=3, columnspan=2, sticky=W)
        # number of cells option menu
        # http://www.logilab.org/card/pylintfeatures#basic-checker
        # pylint: disable = W0142
        self.numCellOption = OptionMenu(pvSysDataFrame, numCells, *MOD_SIZES)
        # pylint: enable = W0142
        self.numCellOption._name = 'numCellOption'  # IGNORE:W0212
        self.numCellOption.grid(row=3, column=2)

        # slider to explore IV curves
#        _getIV = self.register(self.getIV)
        self.pvSysScale = Scale(pvSysDataFrame, orient=HORIZONTAL,
                                label='I-V Curve', command=self.getIV,
                                from_=0, to=(NPTS - 1))
        self.pvSysScale.grid(row=4, columnspan=3, sticky=(E + W))
        # Isys
        Label(pvSysDataFrame, text='Isys [A]').grid(row=5)
        self.pvIsys = Entry(pvSysDataFrame, textvariable=txtIsys,
                            width=7)
        self.pvIsys.grid(row=6, column=1)
        # Vsys
        Label(pvSysDataFrame, text='Vsys [V]').grid(row=5, column=1)
        self.pvVsys = Entry(pvSysDataFrame, textvariable=txtVsys,
                            width=7)
        self.pvVsys.grid(row=6)
        # Psys
        Label(pvSysDataFrame, text='Psys [kW]').grid(row=5, column=2)
        self.pvPsys = Entry(pvSysDataFrame, textvariable=txtPsys,
                            width=7)
        self.pvPsys.grid(row=6, column=2)

        Label(pvSysDataFrame, text='Imp').grid(row=7)
        Label(pvSysDataFrame, text='Vmp').grid(row=7, column=1)
        Label(pvSysDataFrame, text='Pmp').grid(row=7, column=2)
        self.pvImp = Entry(pvSysDataFrame, textvariable=txtImp,
                            width=7)
        self.pvImp.grid(row=8)
        self.pvVmp = Entry(pvSysDataFrame, textvariable=txtVmp,
                            width=7)
        self.pvVmp.grid(row=8, column=1)
        self.pvPmp = Entry(pvSysDataFrame, textvariable=txtPmp,
                            width=7)
        self.pvPmp.grid(row=8, column=2)
        Label(pvSysDataFrame, text='Isc').grid(row=9)
        Label(pvSysDataFrame, text='Voc').grid(row=9, column=1)
        Label(pvSysDataFrame, text='FF').grid(row=9, column=2)
        self.pvIsc = Entry(pvSysDataFrame, textvariable=txtIsc,
                            width=7)
        self.pvIsc.grid(row=10)
        self.pvVoc = Entry(pvSysDataFrame, textvariable=txtVoc,
                            width=7)
        self.pvVoc.grid(row=10, column=1)
        self.pvFF = Entry(pvSysDataFrame, textvariable=txtFF,
                            width=7)
        self.pvFF.grid(row=10, column=2)

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

    def reset(self):
        # number of strings integer variable
        self.numberStrings.set(10)  # default
        # number of strings integer variable
        self.stringID.set(1)  # default
        # number of modules integer variable
        self.numberModules.set(10)  # default
        # number of cells integer variable
        self.numberCells.set(MOD_SIZES[1])  # default value is 96
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
