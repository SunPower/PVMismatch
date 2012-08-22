# -*- coding: utf-8 -*-
"""
Created on Wed May 30 11:53:52 2012

@author: mmikofski
"""
import numpy as np
import scipy.constants

# defaults
_Rs = 0.004267236774264931  # [ohm] series resistance
_Rsh = 10.01226369025448  # [ohm] shunt resistance
_Isat1 = 2.286188161253440E-11  # [A] diode one saturation current
_Isat2 = 1.117455042372326E-6  # [A] diode two saturation current
_Aph = 1.000426348582935  # photovoltaic current coefficient
_Isc0 = 6  # [A] reference short circuit current
_T = 298.15
_Vbypass = -0.5
_aRBD = 1.036748445065697E-4  # reverse breakdown coefficient
_VRBD = -5.527260068445654  # [V] reverse breakdown voltage
_nRBD = 3.284628553041425  # reverse breakdown exponent
_cellArea = 153.33  # [cm^2] cell area


def npinterpx(x, xp, fp):
    """np.interp function with cubic extrapolation"""
    y = np.interp(x, xp, fp)
    if len(xp) >= 50:
        # extrapolate left
        left = x < xp[0]
        if any(left):
            xleft1 = x[left]
            xleft = np.ones(len(xleft1))
            Aleft = np.ones(5)
            Aleft1 = xp[:5]
            Bleft = fp[:5]
            for dummy in range(3):
                Aleft = Aleft * Aleft1
                Aleft = np.vstack([Aleft, np.ones(5)])
                xleft = xleft * xleft1
                xleft = np.vstack([xleft, np.ones(len(xleft1))])
            Pleft = np.linalg.lstsq(Aleft.T, Bleft.T)
            y[left] = np.dot(Pleft[0], xleft)
#   yleft = fp[0] + (xleft - xp[0]) / (xp[1] - xp[0]) * (fp[1] - fp[0])
#   y[left] = yleft
        # extrapolate right
        right = x > xp[-1]
        if any(right):
            xright1 = x[right]
            xright = np.ones(len(xright1))
            Aright = np.ones(5)
            Aright1 = xp[-5:]
            Bright = fp[-5:]
            for dummy in range(3):
                Aright = Aright * Aright1
                Aright = np.vstack([Aright, np.ones(5)])
                xright = xright * xright1
                xright = np.vstack([xright, np.ones(len(xright1))])
            Pright = np.linalg.lstsq(Aright.T, Bright.T)
            y[right] = np.dot(Pright[0], xright)
#   yright = fp[-1] + (xright - xp[-1]) / (xp[-2] - xp[-1]) * (fp[-2] - fp[-1])
#   y[right] = yright
    return y


class PVconstants(object):
    """
    PVconstants - Class for PV constants
    """
    def __init__(self, Rs=_Rs, Rsh=_Rsh, Isat1=_Isat1, Isat2=_Isat2, Aph=_Aph,
                 Isc0=_Isc0, T=_T, cellArea=_cellArea, Vbypass=_Vbypass,
                 aRBD=_aRBD, VRBD=_VRBD, nRBD=_nRBD):
        self.Rs = Rs
        self.Rsh = Rsh
        self.Isat1 = Isat1
        self.Isat2 = Isat2
        self.Aph = Aph
        self.Isc0 = Isc0
        self.T = T
        self.cellArea = cellArea
        self.Vbypass = Vbypass
        self.aRBD = aRBD
        self.VRBD = VRBD
        self.nRBD = nRBD
        self.k = scipy.constants.k
        self.q = scipy.constants.e
        self.E0 = 1000  # [W/m^2] insolation of 1 sun
