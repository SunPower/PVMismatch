# -*- coding: utf-8 -*-
"""
Created on Jul 29, 2012

@author: marko
"""

from Tkinter import Frame, Label, Button, OptionMenu, IntVar
#from Tkinter import Menu, Entry
MODULE_SIZES = [72, 96, 128]


class PVmodule_tk(Frame):
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

        self['bg'] = 'black'  # set black background
        self['padx'] = '15'  # pad sides with 15 points
        self['pady'] = '5'  # pad top/bottom 5 points
        self.master.title('PVmodule')  # set title bar
        self.SPlogoLabel = Label(self, image=self.pvapp.SPlogo,
                                 cnf={'borderwidth': '0'})
        self.SPlogoLabel.pack({'side': 'top'})

        self.numberCells = IntVar(self)  # bind numberCells
        self.numberCells.set(MODULE_SIZES[0])  # default value
        # pylint: disable = W0142
        self.numberCellsOption = OptionMenu(self, self.numberCells,
                                            *MODULE_SIZES)
        # pylint: enable = W0142
        self.numberCellsOption.pack({'side': 'top', 'fill': 'both'})

        self.QUIT = Button(self, cnf={'text': 'Quit', 'command': self.quit})
        self.QUIT.pack({'side': 'top', 'fill': 'both'})

#        # cell ID # spinbox
#        cellID = self.cellID = IntVar(self)  # bind moduleID
#        cellID.set(1)

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
