# -*- coding: utf-8 -*-
"""
Created on Sep 3, 2012

@author: marko
"""


class PVexception(Exception):
    """
    Base exception class for PVmismatch_tk.
    """
    pass


class PVValidationError(PVexception):
    def __init__(self, argname, argvalue):  # IGNORE:W0231
        self.argname = argname
        self.argvalue = argvalue

    def __str__(self):
        return ('Invalid value, %s, for argument "%s".' % (self.argvalue,
                                                          self.argname))
