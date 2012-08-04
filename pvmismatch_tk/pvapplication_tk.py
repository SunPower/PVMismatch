# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from PIL import Image, ImageTk
from Tkinter import Frame, Label, Button, Toplevel, IntVar, OptionMenu, \
    Message, Spinbox, RIGHT, LEFT, BOTH, W
from pvmismatch_tk.pvmodule_tk import PVmodule_tk
from pvmismatch_tk.pvstring_tk import PVstring_tk
from pvmismatch_tk.pvsystem_tk import PVsystem_tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2TkAgg
from pvmismatch.pvsystem import PVsystem
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


#def spacer(root, width, side):
#    Frame(root, width=width).pack(side=side)


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
        # don't set master.minsize
        master.title(PVAPP_TXT)  # set title bar of master (a.k.a. root)

        # number of strings integer variable
        numStr = self.numberStrings = IntVar(self)
        numStr.set(10)  # default
        # number of strings integer variable
        strID = self.stringID = IntVar(self)
        strID.set(1)  # default
        # number of modules integer variable
        numMod = self.numberModules = IntVar(self)
        numMod.set(10)  # default
        # module ID # integer variable
        modID = self.moduleID = IntVar(self)
        modID.set(1)
        # number of cells integer variable
        numCells = self.numberCells = IntVar(self)  # bind numberCells
        numCells.set(MOD_SIZES[0])  # default value
        # cell ID # spinbox
        cellID = self.cellID = IntVar(self)  # bind moduleID
        cellID.set(1)

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
        pvSysFigCanvas._tkcanvas._name = 'pvSysFigCanvas'
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
#        # string ID label
#        labelCnf = {'name': 'strIDlabel', 'text': 'String ID #'}
#        self.strIDlabel = Label(pvSysFrame, cnf=labelCnf)
#        self.strIDlabel.pack(side=LEFT)
#        spacer(pvSysFrame, 6, LEFT)
#        # string ID # spinbox
#        spinboxCnf = {'name': 'strIDspinbox', 'from_': 1, 'to': MAX_STRINGS,
#                      'textvariable': strID, 'width': 5, 'validate': 'all',
#                      'validatecommand': vcmd, 'invalidcommand': invcmd}
#        self.strIDspinbox = Spinbox(pvSysFrame, cnf=spinboxCnf)
#        self.strIDspinbox.pack(side=LEFT)
#        # PVsystem button
#        self.pvSysButton = Button(pvSysFrame, name='pvsysButton',
#                                     text=PVSYSTEM_TEXT,
#                                     command=self.startPVsystem_tk)
#        self.pvSysButton.pack(side=RIGHT)
#        self.separatorLine()  # separator

#        # PVstring frame
#        pvStrFrame = self.pvStrFrame = Frame(master, name='pvStrFrame')
#        pvStrFrame.pack(fill=BOTH)

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
#        # module ID # label
#        labelCnf = {'name': 'modIDlabel', 'text': 'Module ID #'}
#        self.modIDlabel = Label(pvStrFrame, cnf=labelCnf)
#        self.modIDlabel.pack(side=LEFT)
#        # module ID # spinbox
#        spinboxCnf = {'name': 'modIDspinbox', 'from_': 1, 'to': MAX_MODULES,
#                      'textvariable': modID, 'width': 5, 'validate': 'all',
#                      'validatecommand': vcmd, 'invalidcommand': invcmd}
#        self.modIDspinbox = Spinbox(pvStrFrame, cnf=spinboxCnf)
#        self.modIDspinbox.pack(side=LEFT)
#        # PVmodule button
#        self.pvStrButton = Button(pvStrFrame, cnf={'text': PVSTRING_TEXT})
#        self.pvStrButton.pack(side=RIGHT)
#        self.pvStrButton['command'] = self.startPVstring_tk
#        self.separatorLine()  # separator
#
#        ## PVmodule frame
#        pvModFrame = self.pvModFrame = Frame(master, name='pvModFrame')
#        pvModFrame.pack(fill=BOTH)

        # number of cells label
        labelCnf = {'name': 'numCellLabel', 'text': 'Number of Cells'}
        self.numCellLabel = Label(pvSysDataFrame, cnf=labelCnf)
        self.numCellLabel.grid(row=3, columnspan=2, sticky=W)
        # number of cells option menu
        # http://www.logilab.org/card/pylintfeatures#basic-checker
        # pylint: disable = W0142
        self.numCellOption = OptionMenu(pvSysDataFrame, numCells, *MOD_SIZES)
        # pylint: enable = W0142
        self.numCellOption._name = 'numCellOption'
        self.numCellOption.grid(row=3, column=2)
#        # cell ID # label
#        self.cellIDlabel = Label(pvModFrame, text='Cell ID #')
#        self.cellIDlabel.pack(side=LEFT)
#        spacer(pvModFrame, 16, LEFT)
#        # cell ID spinbox
#        maxModSize = max(MOD_SIZES)
#        spinboxCnf = {'name': 'cellIDspinbox', 'from_': 1, 'to': maxModSize,
#                      'textvariable': cellID, 'width': 5, 'validate': 'all',
#                      'validatecommand': vcmd, 'invalidcommand': invcmd}
#        self.cellIDspinbox = Spinbox(pvModFrame, cnf=spinboxCnf)
#        self.cellIDspinbox.pack(side=LEFT)
#        self.pvModButton = Button(pvModFrame,
#                                     cnf={'text': PVMODULE_TEXT})
#        self.pvModButton.pack(side=RIGHT)
#        self.pvModButton['command'] = self.startPVmodule_tk
#        self.separatorLine()  # separator

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
#        elif W_ == ".pvSysDataFrame.strIDspinbox":
#            maxVal = MAX_STRINGS
        elif W_ == ".pvSysFrame.pvSysDataFrame.numModSpinbox":
            maxVal = MAX_MODULES
#        elif W_ == ".pvSysDataFrame.modIDspinbox":
#            maxVal = MAX_MODULES
#        elif W_ == ".pvSysDataFrame.cellIDspinbox":
#            maxVal = max(MOD_SIZES)
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
#        elif W_ == ".pvSysDataFrame.strIDspinbox":
#            errText = 'Invalid string ID number!'
        elif W_ == ".pvSysFrame.pvSysDataFrame.numModSpinbox":
            errText = 'Invalid number of modules!'
#        elif W_ == ".pvSysDataFrame.modIDspinbox":
#            errText = 'Invalid module ID number!'
#        elif W_ == ".pvSysDataFrame.cellIDspinbox":
#            errText = 'Invalid cell ID number!'
        else:
            pass
        w = self.nametowidget(W_)
        w.config(validate=v)
        self.MESSAGE.config(fg='red', text=errText, width=150)
        self.bell()

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
        # module ID # integer variable
        self.moduleID.set(1)
        # number of cells integer variable
        self.numberCells.set(MOD_SIZES[0])  # default value
        # cell ID # spinbox
        self.cellID.set(1)
        self.MESSAGE.config(fg='black', text=READY_MSG, width=150)
        print 'reset'

    def load(self):
        print 'load *.pv file'

    def save(self):
        print 'save *.pv file'

#    def separatorLine(self):
#        # master is known in constructor, but not here!
#        Frame(self.master, height=2, bg='white').pack(fill=BOTH)

    def _quit(self):
        # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        self.master.quit()  # stops mainloop
        self.master.destroy()
