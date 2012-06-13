# -*- coding: utf-8 -*-
"""
Created on Wed May 30 11:53:52 2012

@author: mmikofski
"""

# defaults
_Rs = 0.004267236774264931  # [ohm] series resistance
_Rsh = 10.01226369025448  # [ohm] shunt resistance
_Isat1 = 2.286188161253440E-11  # [A] diode one saturation current
_Isat2 = 1.117455042372326E-6  # [A] diode two saturation current
_Aph = 1.000426348582935  # photovoltaic current coefficient
_Isc0 = 6  # [A] reference short circuit current
_VRBD = -5.5
_T = 298.15
_Vbypass = -0.5
_aRBD = 1.036748445065697E-4  # reverse breakdown coefficient
_VRBD = -5.527260068445654  # [V] reverse breakdown voltage
_nRBD = 3.284628553041425  # reverse breakdown exponent


def npinterpX(x, xp, fp):
    """np.interp function with linear extrapolation"""
    import numpy as np
    y = np.interp(x, xp, fp)
    y = np.where(x < xp[0],
                 fp[0] + (x - xp[0]) / (xp[1] - xp[0]) * (fp[1] - fp[0]),
                 y)
    y = np.where(x > xp[-1],
                 fp[-1] + (x - xp[-1]) / (xp[-2] - xp[-1]) * (fp[-2] - fp[-1]),
                 y)
    return y


class PVconstants(object):
    """
    PVconstants - Class for PV constants
    """
    def __init__(self, Rs=_Rs, Rsh=_Rsh, Isat1=_Isat1, Isat2=_Isat2, Aph=_Aph,
                 Isc0=_Isc0, T=_T, Vbypass=_Vbypass,
                 aRBD=_aRBD, VRBD=_VRBD, nRBD=_nRBD):
        self.Rs = Rs
        self.Rsh = Rsh
        self.Isat1 = Isat1
        self.Isat2 = Isat2
        self.Aph = Aph
        self.Isc0 = Isc0
        self.T = T
        self.Vbypass = Vbypass
        self.aRBD = aRBD
        self.VRBD = VRBD
        self.nRBD = nRBD
        self.k = 1.380658E-23
        self.q = 1.602176487E-19