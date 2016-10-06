# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from PIL import Image, ImageTk
from Tkconstants import RIGHT, LEFT, BOTH, E, W, HORIZONTAL
from Tkinter import Frame, Label, Button, Toplevel, OptionMenu, Scale, Entry, \
    Message, Spinbox, IntVar, StringVar, DoubleVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2TkAgg
from threading import Thread
from tkFont import nametofont
import Queue
import json
import logging
import numpy as np
import os
from pvmismatch.pvmismatch_lib.pvconstants import MODSIZES, NUMBERCELLS, \
    NUMBERMODS, NUMBERSTRS
from pvmismatch.pvmismatch_lib.pvmodule import STD128, STD72, STD96, STD24
from pvmismatch import PVsystem as PVsystem_cls, PVmodule, PVcell
# use absolute imports instead of relative, so modules are portable
from pvmismatch import __name__ as __pkg_name__, __file__ as __pkg_file__
from pvmismatch.pvmismatch_tk.advCnf_tk import AdvCnf_tk
from pvmismatch.pvmismatch_tk.pvexceptions import PVValidationError
from pvmismatch.pvmismatch_tk.pvstring_tk import PVstring_tk
import webbrowser

INTEGERS = '0123456789'
FLOATS = '.' + INTEGERS
PVAPP_TXT = __pkg_name__
READY_MSG = 'Ready'
LANGUAGE = 'English'
PKG_BASEDIR = os.path.dirname(__pkg_file__)
JSONDIR = os.path.join(PKG_BASEDIR, 'pvmismatch_json')
SPLOGO = os.path.join(PKG_BASEDIR, 'res', 'logo_bg.png')
DOCS = os.path.join(PKG_BASEDIR, 'docs', '_build', 'html', 'index.html')

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s')


class waitWidget(Frame):  # pylint: disable=R0924,R0904
    """
    A wait widget that shows something is happening.
    """
    def __init__(self, queue, master):
        self.queue = queue
        Frame.__init__(self, master)
        self.pack(fill="both")
        self.focus_set()  # get the focus
        self.grab_set()  # make this window modal
        master.resizable(False, False)  # not resizable
        master.title("")  # no title
        # don't let user close window using X - instead call timer
        master.protocol("WM_DELETE_WINDOW", self.timer)
        self.wait = IntVar(master, 0, "wait")
        Label(master, bitmap="hourglass").pack(fill="both")
        Label(master, text="Please wait ...").pack(fill="both")
        Label(master, textvariable=self.wait).pack(fill="both")
        self.timer()

    def timer(self):
        """
        A callback that counts milliseconds until SELF.QUEUE has somthing in it
        """
        wait = self.wait.get() + 1
        if not self.queue.empty():
            # when queue is filled, quit loop and print elapsed time
            logging.debug('elapsed time = %2.1f [s]', wait * 0.10)
            self.quit()
        self.wait.set(wait)
        # loop over this callback every 100[ms] until queue is filled
        self.after(100, self.timer)


def setqueue(original_function, queue):
    """
    Create a new function QUEUEFUN that calculates the results from the
    ORIGINAL_FUNCTION and puts them in a queue.
    :param original_function: The function the results of which are added to \
        the queue.
    :param queue: The queue to which the results of the original_function are \
        added.
    :return queuefun: The new function.
    """
    def queuefun(*args, **kwargs):
        """
        Call ORIGINAL_FUNCTION with ARGS & KWARGS and put the results in QUEUE.
        NOTE: this is function *call*, not a function object!
        This is equivalent to:
        >>> results = original_function(*args, **kwargs)  # calc results
        >>> queue.put(results)  # put results in queue
        >>> results = queue.get()  # get results from queue
        
        """
        logging.debug('Starting')
        queue.put(original_function(*args, **kwargs))
        logging.debug('Exiting')

    return queuefun


def waitbox(original_function):
    """
    Create a new function that adds a waitbox widget to original_function.
    :param original_function: A funciton to wrap with a waitbox waitWidget
    """
    def new_function(*args, **kwargs):
        """
        Create a queue, create a queuefun from original_function and make the
        new queuefun the target of a thread, passing the thread target
        original_function's args and kwargs. Then instantiate a new Tk Toplevel
        Frame called master and a new waitWidget with the queue and master.
        Start master's mainloop which exits when the original_function's
        results are fed to the queue. Destroy master and return the
        original_function's results.
        """
        queue = Queue.Queue()
        queuefun = setqueue(original_function, queue)
        thread = Thread(target=queuefun, args=args, kwargs=kwargs)
        thread.start()
        master = Toplevel()
        waitBox = waitWidget(queue, master)
        waitBox.mainloop()
        master.destroy()
        return queue.get()

    return new_function

PVsystem = waitbox(PVsystem_cls)  # wrap PVsystem with a waitbox waitWidget


class PVapplicaton(Frame):
    """
    classdocs
    """

    def __init__(self, master=None):
        """
        Constructor
        """
        Frame.__init__(self, master, name='pvApplication',
                       bg='black', padx=5, pady=5)
        # set black background, pad sides with 15 points, top/bottom 5 points
        # fill=BOTH fills in padding with background color
        # w/o fill=BOTH padding is default color
        # side=TOP is the default
        self.pack(fill=BOTH)
        master.resizable(False, False)  # not resizable in x or y
        master.title(PVAPP_TXT)  # set title bar of master (a.k.a. root)
        master.protocol("WM_DELETE_WINDOW", self._quit)  # close window to quit

        self.validationConstants = self.readJSON('validationConstants')
        self.messagetext = self.readJSON('messagetext' + '.' + LANGUAGE)
        MAX_STRINGS = self.validationConstants["pvapplication"]["numStrs"]
        MAX_MODULES = self.validationConstants["pvapplication"]["numMods"]
        MAX_SUNS = self.validationConstants["pvapplication"]["sysEe"]
        CAPTION_FONT = nametofont('TkCaptionFont')  # font for titles

        # PVsystem
        pvSys = self.pvSys = PVsystem()

        # variables
        numStrs = self.numStrs = IntVar(self, NUMBERSTRS, 'numStrs')
        numMods = self.numMods = IntVar(self, NUMBERMODS, 'numMods')
        numCells = self.numCells = IntVar(self, NUMBERCELLS, 'numCells')
        txtIsys = self.txtIsys = DoubleVar(self, name='txtIsys')
        txtVsys = self.txtVsys = DoubleVar(self, name='txtVsys')
        txtPsys = self.txtPsys = DoubleVar(self, name='txtPsys')
        txtImp = self.txtImp = StringVar(self, name='txtImp')
        txtVmp = self.txtVmp = StringVar(self, name='txtVmp')
        txtPmp = self.txtPmp = StringVar(self, name='txtPmp')
        txtIsc = self.txtIsc = StringVar(self, name='txtIsc')
        txtVoc = self.txtVoc = StringVar(self, name='txtVoc')
        txtFF = self.txtFF = StringVar(self, name='txtFF')
        txtEff = self.txtEff = StringVar(self, name='txtEff')
        sysEe = self.sysEe = DoubleVar(self, 1, name='sysEe')
        txtImp.set("{:7.3f}".format(self.pvSys.Imp))  # [A]
        txtVmp.set("{:7.3f}".format(self.pvSys.Vmp))  # [V]
        txtPmp.set("{:7.3f}".format(self.pvSys.Pmp / 1000))  # [kW]
        txtIsc.set("{:7.3f}".format(self.pvSys.Isc))  # [A]
        txtVoc.set("{:7.3f}".format(self.pvSys.Voc))  # [V]
        txtFF.set("{:7.3f}".format(self.pvSys.FF * 100))  # [%]
        txtEff.set("{:7.3f}".format(self.pvSys.eff * 100))  # [%]
        self.msgtext = StringVar(self, READY_MSG, 'msgtext')

        # must register vcmd and invcmd as Tcl functions
        vcmd = (self.register(self.validateWidget),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        invcmd = (self.register(self.invalidWidget),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # SP logo
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

        # number of strings
        _row += 1  # row 1
        Label(pvSysDataFrame,
              text='Number of Strings').grid(row=_row, columnspan=2, sticky=W)
        # use textVar to set number of strings from LOAD, RESET or default
        spinboxCnf = {'name': 'numStrSpinbox', 'from_': 1, 'to': MAX_STRINGS,
                      'textvariable': numStrs, 'width': 5, 'validate': 'all',
                      'validatecommand': vcmd, 'invalidcommand': invcmd,
                      'command': self.updatePVsys}
        self.numStrSpinbox = Spinbox(pvSysDataFrame, cnf=spinboxCnf)
        self.numStrSpinbox.bind("<Return>", self.keyBinding)
        self.numStrSpinbox.grid(row=_row, column=2)

        # number of modules
        _row += 1  # row 2
        Label(pvSysDataFrame,
              text='Number of Modules').grid(row=_row, columnspan=2, sticky=W)
        # number of modules spinbox
        spinboxCnf = {'name': 'numModSpinbox', 'from_': 1, 'to': MAX_MODULES,
                      'textvariable': numMods, 'width': 5, 'validate': 'all',
                      'validatecommand': vcmd, 'invalidcommand': invcmd,
                      'command': self.updatePVsys}
        self.numModSpinbox = Spinbox(pvSysDataFrame, cnf=spinboxCnf)
        self.numModSpinbox.bind("<Return>", self.keyBinding)
        self.numModSpinbox.grid(row=_row, column=2)

        # number of cells
        _row += 1  # row 3
        Label(pvSysDataFrame,
              text='Number of Cells').grid(row=_row, columnspan=2, sticky=W)
        # http://www.logilab.org/card/pylintfeatures#basic-checker
        # pylint: disable = W0142
        self.numCellOption = OptionMenu(pvSysDataFrame, numCells, *MODSIZES,
                                        command=self.updatePVsys)
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
        self.pvSysScale = Scale(pvSysDataFrame, orient=HORIZONTAL,
                                label='I-V Curve', font=CAPTION_FONT,
                                command=self.getIV, showvalue=False,
                                from_=0, to=(pvSys.pvconst.npts - 1))
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

        # set suns
        _row += 6  # row 13
        Label(pvSysDataFrame, text='Irradiance [suns]',
              font=CAPTION_FONT).grid(row=_row, columnspan=2, sticky=W)
        # number of modules spinbox
        spinboxCnf = {'name': 'sunSpinbox', 'from_': 0.2, 'to': MAX_SUNS,
                      'increment': 0.1, 'textvariable': sysEe, 'width': 5,
                      'validate': 'all', 'validatecommand': vcmd,
                      'invalidcommand': invcmd, 'command': self.updatePVsys}
        self.sunSpinbox = Spinbox(pvSysDataFrame, cnf=spinboxCnf)
        self.sunSpinbox.bind("<Return>", self.keyBinding)
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
        self.SAVE = Button(toolbar, text='Save', command=self._save)
        self.SAVE.pack(side=RIGHT)
        self.LOAD = Button(toolbar, text='Load', command=self._load)
        self.LOAD.pack(side=RIGHT)
        self.RESET = Button(toolbar, text='Reset', command=self._reset)
        self.RESET.pack(side=RIGHT)
        self.UPDATE = Button(toolbar, text='Update', command=self._update)
        self.UPDATE.pack(side=RIGHT)
        self.HELP = Button(toolbar, text='Help', command=self._help)
        self.HELP.pack(side=RIGHT)
        self.MESSAGE = Message(toolbar, textvariable=self.msgtext,
                               width=500, fg='red')
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
        logging.debug("OnValidate: d={}, i={}, P={}, s={}, S={}, v={}, V={}, W={}".format(*args))
        if W_ == ".pvSysFrame.pvSysDataFrame.numStrSpinbox":
            valType = INTEGERS
            valTest = lambda val: int(val)  # IGNORE:W0108
        elif W_ == ".pvSysFrame.pvSysDataFrame.numModSpinbox":
            valType = INTEGERS
            valTest = lambda val: int(val)  # IGNORE:W0108
        elif W_ == ".pvSysFrame.pvSysDataFrame.sunSpinbox":
            valType = FLOATS
            valTest = lambda val: float(val)  # IGNORE:W0108
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
        logging.debug("OnInvalid: d={}, i={}, P={}, s={}, S={}, v={}, V={}, W={}".format(*args))
        if W_ == ".pvSysFrame.pvSysDataFrame.numStrSpinbox":
            errText = 'Invalid number of strings!'
        elif W_ == ".pvSysFrame.pvSysDataFrame.numModSpinbox":
            errText = 'Invalid number of modules!'
        elif W_ == ".pvSysFrame.pvSysDataFrame.sunSpinbox":
            errText = 'Invalid irradiance!'
        else:
            errText = 'Unknown widget!'
        w = self.nametowidget(W_)
        w.config(validate=v)
        self.msgtext.set(errText)
        self.bell()

    def getIV(self, *args):
        logging.debug('args:\n\t%r', args)
        x = np.float64(float(args[0]) / self.pvSys.pvconst.npts / 2.)
        xp = np.concatenate((self.pvSys.pvconst.negpts, self.pvSys.pvconst.pts),
                            axis=0).flatten()
        Vsys = np.interp(x, xp, self.pvSys.Vsys)
        Isys = np.interp(x, xp, self.pvSys.Isys)
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
        """
        open advnaced config window
        """
        top = Toplevel(name='advCnfTop')
        app = AdvCnf_tk(self, top)
        app.mainloop()
        # please destroy me or I'll continue to run in background
        top.destroy()

    def keyBinding(self, event):
        logging.debug('event widget:\n\t%r', event.widget)
        logging.debug('event widget get:\n\t%r', event.widget.get())
        self.updatePVsys()

    def updatePVsys(self, *args, **kwargs):
        logging.debug('args:\n\t%r', args)
        logging.debug('kwargs:\n\t%r', kwargs)
        if args and isinstance(args[0], PVsystem_cls):
            pvsys = args[0]
            for n, pvstr in enumerate(pvsys.pvstrs):
                for pvmod in pvstr.pvmods:
                    pvmod.calcMod()
                pvstr.calcString()
                logging.debug('updating pvstring #%d: Pmp = %g[W]', n, pvstr.Pstring.max())
            return
        PVAPP = "pvapplication"
        try:
            numStrs = self.numStrs.get()
            if not (0 < numStrs <= self.validationConstants[PVAPP]["numStrs"]):
                raise PVValidationError('numStrs', numStrs)
            numMods = self.numMods.get()
            if not (0 < numMods <= self.validationConstants[PVAPP]["numMods"]):
                raise PVValidationError('numMods', numMods)
            sysEe = self.sysEe.get()
            if not (0 < sysEe <= self.validationConstants[PVAPP]["sysEe"]):
                raise PVValidationError('sysEe', sysEe)
        except PVValidationError as err:
            logging.debug('err:\n\t%r', err)
            errtext = self.messagetext[PVAPP][err.argname]
            self.msgtext.set(errtext)
            self.bell()
            return
        numCells = self.numCells.get()
        self.msgtext.set(self.messagetext[PVAPP]["Ready"])
        pvconst = self.pvSys.pvconst
        pvcell = PVcell(Ee=sysEe)
        if numCells == 24:
            numCells = STD24
        elif numCells == 72:
            numCells = STD72
        elif numCells == 96:
            numCells = STD96
        elif numCells == 128:
            numCells = STD128
        pvmods = PVmodule(cell_pos=numCells, pvcells=pvcell)
        self.pvSys = PVsystem(pvconst, numStrs, numberMods=numMods,
                              pvmods=pvmods)
        self.updateIVstats()


    def updateIVstats(self):
        # reuse sysPlot figure and update pvSysFigCanvas
        self.pvSysPlot = self.pvSys.plotSys(self.pvSysPlot)
        self.pvSysFigCanvas.show()
        self.txtImp.set("{:7.3f}".format(self.pvSys.Imp))  # [A]
        self.txtVmp.set("{:7.3f}".format(self.pvSys.Vmp))  # [V]
        self.txtPmp.set("{:7.3f}".format(self.pvSys.Pmp / 1000))  # [kW]
        self.txtIsc.set("{:7.3f}".format(self.pvSys.Isc))  # [A]
        self.txtVoc.set("{:7.3f}".format(self.pvSys.Voc))  # [V]
        self.txtFF.set("{:7.3f}".format(self.pvSys.FF * 100))  # [%]
        self.txtEff.set("{:7.3f}".format(self.pvSys.eff * 100))  # [%]

    def _help(self):
        logging.debug('show docs in browser')
        webbrowser.open(DOCS)

    def _update(self):
        self.msgtext.set(READY_MSG)
        self.updatePVsys()

    def _reset(self):
        # number of strings integer variable
        self.numStrs.set(NUMBERSTRS)  # default
        # number of modules integer variable
        self.numMods.set(NUMBERMODS)  # default
        # number of cells integer variable
        self.numCells.set(NUMBERCELLS)  # default value is 96
        self.msgtext.set(READY_MSG)
        # TODO: need to reset advCnf too
        logging.debug('reset')

    def _load(self):
        logging.debug('load *.pv file')

    def _save(self):
        logging.debug('save *.pv file')

    def _quit(self):
        # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        self.master.quit()  # stops mainloop
        self.master.destroy()

    def readJSON(self, JSONfilename):
        if not JSONfilename.endswith('json'):
            JSONfilename += '.json'
        JSONfullpath = os.path.join(JSONDIR, JSONfilename)
        with open(JSONfullpath, 'r') as JSONfile:
            JSONObjects = json.load(JSONfile)
            logging.debug('JSON objects loaded from %s.', JSONfullpath)
        return JSONObjects
