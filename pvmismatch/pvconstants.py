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
_T = 298.15  # [K] cell temperature
_Vbypass = -0.5  # [V] trigger voltage of bypass diode
_aRBD = 1.036748445065697E-4  # reverse breakdown coefficient
_VRBD = -5.527260068445654  # [V] reverse breakdown voltage
_nRBD = 3.284628553041425  # reverse breakdown exponent
_cellArea = 153.33  # [cm^2] cell area


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
    def __init__(self, Rs=_Rs, Rsh=_Rsh, Isat1=_Isat1, Isat2=_Isat2, Aph=_Aph,
                 Isc0=_Isc0, T=_T, cellArea=_cellArea, Vbypass=_Vbypass,
                 aRBD=_aRBD, VRBD=_VRBD, nRBD=_nRBD):
        self.Rs = Rs  # [ohm] series resistance
        self.Rsh = Rsh  # [ohm] shunt resistance
        self.Isat1 = Isat1  # [A] diode one saturation current
        self.Isat2 = Isat2  # [A] diode two saturation current
        self.Aph = Aph  # photovoltaic current coefficient
        self.Isc0 = Isc0  # [A] reference short circuit current
        self.T = T  # [K] cell temperature
        self.cellArea = cellArea  # [cm^2] cell area
        self.Vbypass = Vbypass  # [V] trigger voltage of bypass diode
        self.aRBD = aRBD  # reverse breakdown coefficient
        self.VRBD = VRBD  # [V] reverse breakdown voltage
        self.nRBD = nRBD  # reverse breakdown exponent
        self.k = scipy.constants.k  # [kJ/mole/K] Boltzmann constant
        self.q = scipy.constants.e  # [Coloumbs] elementary charge
        self.E0 = 1000  # [W/m^2] irradiance of 1 sun

    def update(self, *args, **kwargs):
        kw = ['Rs', 'Rsh', 'Isat1', 'Isat2', 'Aph', 'Isc0', 'T', 'cellArea',
              'Vbypass', 'aRBD', 'VRBD', 'nRBD']
        key = 0
        for val in args:
            self.__setattr__(kw[key], val)
            key += 1
        for key in kwargs:
            if key in kw:
                self.__setattr__(key, kwargs[key])
