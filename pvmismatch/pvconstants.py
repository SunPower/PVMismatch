# -*- coding: utf-8 -*-
"""
Created on Wed May 30 11:53:52 2012

@author: mmikofski
"""

# defaults
_Rs = 0.004267237
_Rsh = 10.01226369
_Isat1 = 2.28619E-11
_Isat2 = 1.11746E-06
_Aph = 1.000426349
_Isc0 = 6
_VRBD = -5.5
_T = 298.15
_Vbypass = -0.5


def extrap(x, xp, fp, left=True):
    import numpy as np
    try:
        x = np.array(x, dtype=float)
        xp = np.array(xp, dtype=float)
        fp = np.array(fp, dtype=float)
    except ValueError as error:
        print error
    if type(left) is not bool:
        # TODO raise exception
        print "left must be boolean!"
    if left:
        x = x[x < xp[0]]
        xp = xp[:2]
        fp = fp[:2]
    else:
        x = x[x > xp[0]]
        xp = xp[-2:]
        fp = fp[-2:]
    return fp[0] + (x - xp[0]) / (xp[1] - xp[0]) * (fp[1] - fp[0])


class PVconstants(object):
    """
    PVconstants - Class for PV constants
    """
    def __init__(self, Rs=_Rs, Rsh=_Rsh, Isat1=_Isat1, Isat2=_Isat2, Aph=_Aph,
                 Isc0=_Isc0, VRBD=_VRBD, T=_T, Vbypass=_Vbypass):
        self.Rs = Rs
        self.Rsh = Rsh
        self.Isat1 = Isat1
        self.Isat2 = Isat2
        self.Aph = Aph
        self.Isc0 = Isc0
        self.T = T
        self.Vbypass = Vbypass
        self.k = 1.3807E-23
        self.q = 1.6022E-19