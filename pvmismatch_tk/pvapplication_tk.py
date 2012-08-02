# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""
from PIL import Image, ImageTk
from Tkinter import StringVar, Frame, Label, Button, Toplevel, IntVar, \
    OptionMenu, Message, Spinbox, RIGHT, LEFT, BOTH, W
from pvmismatch_tk.pvmodule_tk import PVmodule_tk
from pvmismatch_tk.pvstring_tk import PVstring_tk
from pvmismatch_tk.pvsystem_tk import PVsystem_tk
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


def spacer(root, width, side):
    Frame(root, width=width).pack(side=side)


class PVapplicaton(Frame):
    """
    classdocs
    """

    def __init__(self, master=None):
        """
        Constructor
        """
        Frame.__init__(self, master)
        self._name = 'pvApplication'  # set name of frame widget
        master.resizable(False, False)  # not resizable in x or y
        # don't set master.minsize
        master.title(PVAPP_TXT)  # set title bar of master (a.k.a. root)
        # set black background, pad sides with 15 points, top/bottom 5 points
        self.config(bg='black', padx=5, pady=5)
        # fill=BOTH fills in padding with background color
        # w/o fill=BOTH padding is default color
        # side=TOP is the default
        self.pack(fill=BOTH)

        # number of strings integer variable
        numStr = self.numberStrings = IntVar(self)
        numStr.set(10)  # default
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
        self.cellID.set(1)

        # SP logo
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
        introtext = 'PVmismatch calculates I-V and P-V curves as well as the'
        introtext += '  max power point (MPP) for any sized system.'
        # anchor=W aligns message on left side, NW is no different
        # fg='white' sets text color to white, default is black, so it doesn't
        #   show on black background
        # default aspect is 150%, about as wide as high, or set width>0
        self.introMsg = Message(self, name='introMsg', text=introtext,
                                width=285, bg='black', fg='white', anchor=W)
        # fill=BOTH expands the message to fill parent frame
        # w/o fill=BOTH message is centered in frame even with anchor=W
        self.introMsg.pack(fill=BOTH)
        self.separatorLine()  # separator

        # PVsystem frame
        pvSysFrame = self.PVsystemFrame = Frame(master, name='pvSysFrame')
        # fill=BOTH keeps widgets in frame on left when window is resized
        pvSysFrame.pack(fill=BOTH)
        # number of strings label
        labelCnf = {'name': 'numStrLabel', 'text': 'Number of Strings'}
        self.numberStringsLabel = Label(pvSysFrame, cnf=labelCnf)
        self.numberStringsLabel.pack(side=LEFT)
        spacer(pvSysFrame, 6, LEFT)
        # number of strings spinbox
        # use textVar to set number of strings from LOAD, RESET or default
        spinboxCnf = {'name': 'numStrSpinbox', 'from_': 1, 'to': MAX_STRINGS,
                      'textvariable': numStr, 'width': 5}
        self.numberStringsSpinbox = Spinbox(pvSysFrame, cnf=spinboxCnf)
        self.numberStringsSpinbox.pack(side=LEFT)
        # PVsystem button
        self.PVsystemButton = Button(pvSysFrame, name='pvsysButton',
                                     text=PVSYSTEM_TEXT,
                                     command=self.startPVsystem_tk)
        self.PVsystemButton.pack(side=RIGHT)
        self.separatorLine()  # separator

        # PVstring frame
        pvStrFrame = self.PVstringFrame = Frame(master, name='pvStrFrame')
        pvStrFrame.pack(fill=BOTH)
        # number of modules label
        labelCnf = {'name': 'numModLabel', 'text': 'Number of Modules'}
        self.numberModulesLabel = Label(pvStrFrame, cnf=labelCnf)
        self.numberModulesLabel.pack(side=LEFT)
        # number of modules spinbox
        # must register vcmd and invcmd as Tcl functions
        vcmd = (self.register(self.validateNumberModules),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        invcmd = (self.register(self.invalidNumberModules),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        spinboxCnf = {'name': 'numModSpinbox', 'from_': 1, 'to': MAX_MODULES,
                      'textvariable': numMod, 'width': 5, 'validate': 'focusout',
                      'validatecommand': vcmd, 'invalidcommand': invcmd}
        self.numberModulesSpinbox = Spinbox(pvStrFrame, cnf=spinboxCnf)
        self.numberModulesSpinbox.pack(side=LEFT)
        # module ID # label
        self.modIDLabel = Label(pvStrFrame, text='Module ID #')
        self.modIDLabel.pack(side=LEFT)
        # module ID # spinbox
        # must register vcmd and invcmd as Tcl functions
        vcmd = (self.register(self.validateModuleID),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        invcmd = (self.register(self.invalidModuleID),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        spinboxCnf = {'name': 'modIDspinbox', 'from_': 1, 'to': numMod.get(),
                      'textvariable': modID, 'width': 5, 'validate': 'focusout',
                      'validatecommand': vcmd, 'invalidcommand': invcmd}
        self.modIDspinbox = Spinbox(pvStrFrame, cnf=spinboxCnf)
        self.modIDspinbox.pack(side=LEFT)
        # PVmodule button
        self.PVstringButton = Button(pvStrFrame, cnf={'text': PVSTRING_TEXT})
        self.PVstringButton.pack(side=RIGHT)
        self.PVstringButton['command'] = self.startPVstring_tk
        self.separatorLine()  # separator

        ## PVmodule frame
        pvModFrame = self.PVmoduleFrame = Frame(master)
        pvModFrame.pack(fill=BOTH)
        # number of cells label
        labelCnf = {'name': 'numCellsLabel', 'text': 'Number of Cells'}
        self.numberCellsLabel = Label(pvModFrame, cnf=labelCnf)
        self.numberCellsLabel.pack(side=LEFT)
        spacer(pvModFrame, 6, LEFT)
        # number of cells option menu
        # http://www.logilab.org/card/pylintfeatures#basic-checker
        # pylint: disable = W0142
        self.numberCellsOption = OptionMenu(pvModFrame, numCells, *MOD_SIZES)
        # pylint: enable = W0142
        self.numberCellsOption.pack(side=LEFT)
        # cell ID # label
        self.cellIDlabel = Label(pvModFrame, text='Cell ID #')
        self.cellIDlabel.pack(side=LEFT)
        spinboxCnf = {'from_': 1, 'to': 72,
                      'textvariable': cellID, 'width': 5}
        self.cellIDspinbox = Spinbox(pvModFrame, cnf=spinboxCnf)
        self.cellIDspinbox.pack(side=LEFT)
        self.PVmoduleButton = Button(pvModFrame,
                                     cnf={'text': PVMODULE_TEXT})
        self.PVmoduleButton.pack(side=RIGHT)
        self.PVmoduleButton['command'] = self.startPVmodule_tk
        self.separatorLine()  # separator

        # toolbar
        toolbar = self.toolbarframe = Frame(master)
        toolbar.pack(fill=BOTH)
        self.QUIT = Button(toolbar, cnf={'text': 'Quit', 'command': self.quit})
        self.QUIT.pack(side=RIGHT)
        self.SAVE = Button(toolbar, cnf={'text': 'Save', 'command': self.save})
        self.SAVE.pack(side=RIGHT)
        self.LOAD = Button(toolbar, cnf={'text': 'Load', 'command': self.load})
        self.LOAD.pack(side=RIGHT)
        self.RESET = Button(toolbar, text='Reset')
        self.RESET['command'] = self.reset
        self.RESET.pack(side=RIGHT)
        self.MESSAGE = Message(toolbar, text='ready')
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

# TODO Fix these functions so that delete and overwrite work

    def validateNumberModules(self, action, index, value_if_allowed,
                              prior_value, text, validation_type,
                              trigger_type, widget_name):
        subst = (action, index, value_if_allowed, prior_value, text,
                 validation_type, trigger_type, widget_name)
        print "OnValidate:",
        print("d={}, i={}, P={}, s={}, S={}, v={}, V={}, W={}".format(*subst))
        if text in INTEGERS:
            try:
                modNum = int(value_if_allowed)
            except ValueError:
                return False
            return 0 < modNum <= MAX_MODULES
        else:
            return False

    def invalidNumberModules(self, *args):
        self.invalidModuleID(*args)

    def validateModuleID(self, action, index, value_if_allowed,
                              prior_value, text, validation_type,
                              trigger_type, widget_name):
        subst = (action, index, value_if_allowed, prior_value, text,
                 validation_type, trigger_type, widget_name)
        print "OnValidate:",
        print("d={}, i={}, P={}, s={}, S={}, v={}, V={}, W={}".format(*subst))
        if text in INTEGERS:
            try:
                modID = int(value_if_allowed)
            except ValueError:
                return False
            return 0 < modID <= self.numberModules.get()
        else:
            return False

    def invalidModuleID(self, action, index, value_if_allowed,
                             prior_value, text, validation_type,
                             trigger_type, widget_name):
        subst = (action, index, value_if_allowed, prior_value, text,
                 validation_type, trigger_type, widget_name)
        print "OnInvalid: ",
        print("d={}, i={}, P={}, s={}, S={}, v={}, V={}, W={}".format(*subst))
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
        print 'reset'

    def load(self):
        print 'load *.pv file'

    def save(self):
        print 'save *.pv file'

    def separatorLine(self):
        # master is known in constructor, but not here!
        Frame(self.master, height=2, bg='white').pack(fill=BOTH)
