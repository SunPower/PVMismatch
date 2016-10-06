# -*- coding: utf-8 -*-
"""
Created on Jul 30, 2012

@author: mmikofski
"""

from Tkinter import Frame, Label, Button, Toplevel
#from Tkinter import IntVar
#import tkFont
# use absolute imports instead of relative, so modules are portable
from pvmismatch.pvmismatch_tk.pvmodule_tk import PVmodule_tk


class PVstring_tk(Frame):
    """
    classdocs
    """

    def __init__(self, pvapp, top):
        """
        Constructor
        """
        self.pvapp = pvapp
        Frame.__init__(self, top)
        self.pack(expand=True)  # if user resizes, expand Frame
        self.pack(fill='both')
        self.focus_set()  # get the focus
        self.grab_set()  # make this window modal
        top.resizable(False, False)  # not resizable in x or y
        top.title('PVstring')  # set title bar
        top.protocol("WM_DELETE_WINDOW", self.quit)  # close window to quit
#        CAPTION_FONT = tkFont.nametofont('TkCaptionFont')  # font for titles
        # number of strings integer variable
#        strID = self.strID = IntVar(self, 1, 'strID')
        # number of strings integer variable
#        self.strID.set(1)  # default

        self['bg'] = 'black'  # set black background
        self['padx'] = '15'  # pad sides with 15 points
        self['pady'] = '5'  # pad top/bottom 5 points
        self.SPlogoLabel = Label(self, image=self.pvapp.SPlogo,
                                 cnf={'borderwidth': '0'})
        self.SPlogoLabel.pack({'side': 'top'})
        self.QUIT = Button(self, cnf={'text': 'Quit', 'command': self.quit})
        self.QUIT.pack({'side': 'top', 'fill': 'both'})

    def startPVmodule_tk(self):
        top = Toplevel()
        app = PVmodule_tk(self, top)
        app.mainloop()
        # please destroy me or I'll continue to run in background
        top.destroy()


#        # module ID # integer variable
#        modID = self.moduleID = IntVar(self)
#        modID.set(1)

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
