# -*- coding: utf-8 -*-
"""
Created on Wed May 30 11:53:52 2012

@author: mmikofski
"""
import numpy as np
import scipy.constants

# defaults
RS = 0.004267236774264931  # [ohm] series resistance
RSH = 10.01226369025448  # [ohm] shunt resistance
ISAT1 = 2.286188161253440E-11  # [A] diode one saturation current
ISAT2 = 1.117455042372326E-6  # [A] diode two saturation current
APH = 1.000426348582935  # photovoltaic current coefficient
ISC0 = 6  # [A] reference short circuit current
TCELL = 298.15  # [K] cell temperature
VBYPASS = -0.5  # [V] trigger voltage of bypass diode
ARBD = 1.036748445065697E-4  # reverse breakdown coefficient
VRBD_ = -5.527260068445654  # [V] reverse breakdown voltage
NRBD = 3.284628553041425  # reverse breakdown exponent
CELLAREA = 153.33  # [cm^2] cell area

# Constants
NPTS = 101  # number of I-V points to calculate
#PTS = np.linspace(0, 1, NPTS).reshape(NPTS, 1)  # IGNORE:E1103
MODSIZES = [72, 96, 128]  # list of possible number of cells per module
SUBSTRSIZES = [[24, 24, 24], [24, 48, 24], [32, 64, 32]]
NUMBERCELLS = MODSIZES[1]  # default number of cells
NUMBERMODS = 10  # default number of modules
NUMBERSTRS = 10  # default number of strings


def npinterpx(x, xp, fp):
    """np.interp function with linear extrapolation"""
    y = np.interp(x, xp, fp)
    # extrapolate left
    left = x < xp[0]
    xleft = x[left]
    yleft = fp[0] + (xleft - xp[0]) / (xp[1] - xp[0]) * (fp[1] - fp[0])
    y[left] = yleft
    # extrapolate right
    right = x > xp[-1]
    xright = x[right]
    yright = fp[-1] + (xright - xp[-1]) / (xp[-2] - xp[-1]) * (fp[-2] - fp[-1])
    y[right] = yright
    return y


class PVconstants(object):
    """
    PVconstants - Class for PV constants
    """
    def __init__(self, Rs=RS, Rsh=RSH, Isat1=ISAT1, Isat2=ISAT2, Aph=APH,
                 Isc0=ISC0, Tcell=TCELL, cellArea=CELLAREA, Vbypass=VBYPASS,
                 aRBD=ARBD, VRBD=VRBD_, nRBD=NRBD, npts=NPTS):
        self.Rs = Rs  # [ohm] series resistance
        self.Rsh = Rsh  # [ohm] shunt resistance
        self.Isat1 = Isat1  # [A] diode one saturation current
        self.Isat2 = Isat2  # [A] diode two saturation current
        self.Aph = Aph  # photovoltaic current coefficient
        self.Isc0 = Isc0  # [A] reference short circuit current
        self.Tcell = Tcell  # [K] cell temperature
        self.cellArea = cellArea  # [cm^2] cell area
        self.Vbypass = Vbypass  # [V] trigger voltage of bypass diode
        self.aRBD = aRBD  # reverse breakdown coefficient
        self.VRBD = VRBD  # [V] reverse breakdown voltage
        self.nRBD = nRBD  # reverse breakdown exponent
        self.k = scipy.constants.k  # [kJ/mole/K] Boltzmann constant
        self.q = scipy.constants.e  # [Coloumbs] elementary charge
        self.E0 = 1000  # [W/m^2] irradiance of 1 sun
        # set number of points in IV curve(s)
        self.npts = npts  # number of points
        # decrease point spacing as voltage approaches Voc by using logspace
        pts = (11. - np.logspace(1, 0, npts - 1)) / 10.  # point spacing
        self.pts = np.append(0, pts).reshape(NPTS, 1)  # IGNORE:E1103

    def update(self, *args, **kwargs):
        kw = ['Rs', 'Rsh', 'Isat1', 'Isat2', 'Aph', 'Isc0', 'Tcell',
              'cellArea', 'Vbypass', 'aRBD', 'VRBD', 'nRBD']
        key = 0
        for val in args:
            self.__setattr__(kw[key], val)
            key += 1
        for key in kwargs:
            if key in kw:
                self.__setattr__(key, kwargs[key])
