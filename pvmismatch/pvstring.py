# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 14:07:12 2012

@author: mmikofski
"""

import numpy as np
from pvconstants import PVconstants
from pvmodule import PVmodule
from matplotlib import pyplot as plt

_numberMods = 10  # default number of modules


class PVstring(object):
    """
    PVstring - A class for PV strings.
    """

    def __init__(self, pvmods=PVmodule(), numberMods=_numberMods):
        """
        Constructor
        """
        self.numberMods = numberMods
        self.pvmods = pvmods