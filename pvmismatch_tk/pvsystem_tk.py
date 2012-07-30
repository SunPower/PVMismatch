# -*- coding: utf-8 -*-
"""
Created on Jul 28, 2012

@author: marko
"""

from Tkinter import Frame, Label, Button


class PVsystem_tk(Frame):
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
        self.master.title('PVsystem')  # set title bar
        self.SPlogoLabel = Label(self, image=self.pvapp.SPlogo,
                                 cnf={'borderwidth': '0'})
        self.SPlogoLabel.pack({'side': 'top'})
        self.QUIT = Button(self, cnf={'text': 'Quit', 'command': self.quit})
        self.QUIT.pack({'side': 'top', 'fill': 'both'})
