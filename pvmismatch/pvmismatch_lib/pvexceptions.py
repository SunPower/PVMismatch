"""
Created on Mar 26, 2013

@author: mmikofski
"""


class PVexception(Exception):
    """
    Base exception class for pvmismatch.
    """
    pass


class PVparallel_calcError(PVexception):
    def __init__(self, name):  # IGNORE:W0231
        self.name = name

    def __str__(self):
        errmsg = ('Parallel function from module, %s, must be on the main' +
                  ' thread.')
        return errmsg % self.name
