# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 14:07:12 2012

@author: mmikofski
"""

import numpy as np
# from pvconstants import PVconstants
from pvmodule import PVmodule
from matplotlib import pyplot as plt

_numberMods = 10  # default number of modules


class PVstring(object):
    """
    PVstring - A class for PV strings.
    """

    def __init__(self, pvmods=None, numberMods=_numberMods):
        """
        Constructor
        """
        self.numberMods = numberMods
        if pvmods is None:
            self.pvmods = []  # empty list
            for pvmod in range(self.numberMods):
                self.pvmods.append = PVmodule()
        elif (type(pvmods) is list) & (len(pvmods) == self.numberMods):
            self.pvmods = pvmods
        else:
            # TODO raise exception
            print "Invalid modules list!"

    def calcString(self):
        