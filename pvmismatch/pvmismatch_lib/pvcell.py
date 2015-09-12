# -*- coding: utf-8 -*-

"""
This module contains the :class:`~pvmismatch.pvmismatch_lib.pvcell.PVcell`
object which is used by modules, strings and systems.
"""
import numpy as np
from pvmismatch.pvmismatch_lib.pvconstants import PVconstants
from scipy.optimize import fsolve

# Defaults
RS = 0.004267236774264931  # [ohm] series resistance
RSH = 10.01226369025448  # [ohm] shunt resistance
ISAT1_T0 = 2.286188161253440E-11  # [A] diode one saturation current
ISAT2 = 1.117455042372326E-6  # [A] diode two saturation current
APH = 1.000426348582935  # photovoltaic current coefficient
ISC0_T0 = 6.3056  # [A] reference short circuit current
TCELL = 298.15  # [K] cell temperature
VBYPASS = -0.5  # [V] trigger voltage of bypass diode
ARBD = 1.036748445065697E-4  # reverse breakdown coefficient
VRBD_ = -5.527260068445654  # [V] reverse breakdown voltage
NRBD = 3.284628553041425  # reverse breakdown exponent
CELLAREA = 153.33  # [cm^2] cell area
EG = 1.1  # [eV] band gap of cSi
ALPHA_ISC = 0.0003551  # [1/K] short circuit current temperature coefficient


class PVcell(object):
    """
    PVconstants - Class for PV constants
    """
    def __init__(self, Rs=RS, Rsh=RSH, Isat1_T0=ISAT1_T0, Isat2=ISAT2,
                 Isc0_T0=ISC0_T0, Tcell=TCELL, cellArea=CELLAREA,
                 Vbypass=VBYPASS, aRBD=ARBD, VRBD=VRBD_, nRBD=NRBD, Eg=EG,
                 alpha_Isc=ALPHA_ISC, Ee=1., pvconst=PVconstants()):
        # user inputs
        self.Ee = float(Ee)  #: [suns] incident effective irradiance on cell
        self.pvconst = pvconst  #: configuration constants
        self.Eg = float(Eg)  #: [eV] band gap of cSi
        self.alpha_Isc = float(alpha_Isc)  #: [1/K] short circuit temp. coeff.
        self.Tcell = float(Tcell)  #: [K] cell temperature
        self.Rs = float(Rs)  #: [ohm] series resistance
        self.Rsh = float(Rsh)  #: [ohm] shunt resistance
        self.Isat1_T0 = float(Isat1_T0)  #: [A] diode one sat. current at T0
        # Isat1(Tcell) is a property
        self.Isat2 = float(Isat2)  #: [A] diode two saturation current
        # Aph is a property
        self.Isc0_T0 = float(Isc0_T0)  #: [A] short circuit current at T0
        # Isc(E0, Tcell) is a property
        self.cellArea = float(cellArea)  #: [cm^2] cell area
        self.Vbypass = float(Vbypass)  #: [V] trigger voltage of bypass diode
        self.aRBD = float(aRBD)  #: reverse breakdown coefficient
        self.VRBD = float(VRBD)  #: [V] reverse breakdown voltage
        self.nRBD = float(nRBD)  #: reverse breakdown exponent
        # Voc(Ee, Tcell) is a property
        # IVcurve(Ee, Tcell) is a property

    def __str__(self):
        fmt = '<PVcell(Ee=%g[suns], Tcell=%g[K], Isc=%g[A], Voc=%g[V])>'
        return fmt % (self.Ee, self.Tcell, self.Isc0 * self.Ee, self.Voc)

    def __repr__(self):
        return str(self)

    def __setattr__(self, key, value):
        if key not in ['pvconst']:
            value = float(value)
        super(PVcell, self).__setattr__(key, value)

    def update(self, **kwargs):
        """
        Update user-defined constants.
        """
        # or use __dict__.update(kwargs)
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @property
    def Vt(self):
        """
        Thermal voltage in volts.
        """
        return self.pvconst.k * self.Tcell / self.pvconst.q

    @property
    def Aph(self):
        """
        Photogenerated current coefficient, non-dimensional.
        """
        # short current (SC) conditions (Vcell = 0)
        Isc = self.Ee * self.Isc0
        Vdiode_sc = Isc * self.Rs  # diode voltage at SC
        Idiode1_sc = self.Isat1 * (np.exp(Vdiode_sc / self.Vt) - 1.)
        Idiode2_sc = self.Isat2 * (np.exp(Vdiode_sc / 2. / self.Vt) - 1.)
        Ishunt_sc = Vdiode_sc / self.Rsh  # diode voltage at SC
        # photogenerated current coefficient
        return 1. + (Idiode1_sc + Idiode2_sc + Ishunt_sc) / Isc

    @property
    def Isat1(self):
        """
        Diode one saturation current at Tcell in amps.
        """
        _Tstar = self.Tcell ** 3. / self.pvconst.T0 ** 3.  # scaled temperature
        _inv_delta_T = 1. / self.pvconst.T0 - 1. / self.Tcell  # [1/K]
        _expTstar = np.exp(
            self.Eg * self.pvconst.q / self.pvconst.k * _inv_delta_T
        )
        return self.Isat1_T0 * _Tstar * _expTstar  # [A] Isat1(Tcell)

    @property
    def Isc0(self):
        """
        Short circuit current at Tcell in amps.
        """
        _delta_T = self.Tcell - self.pvconst.T0  # [K] temperature difference
        return self.Isc0_T0 * (1. + self.alpha_Isc * _delta_T)  # [A] Isc0

    @property
    def Voc(self):
        """
        Estimate open circuit voltage of cells.
        Returns Voc : numpy.ndarray of float, estimated open circuit voltage
        """
        C = self.Aph * self.Isc0 * self.Ee + self.Isat1 + self.Isat2
        delta = self.Isat2 ** 2. + 4. * self.Isat1 * C
        return self.Vt * np.log(
            ((-self.Isat2 + np.sqrt(delta)) / 2. / self.Isat1) ** 2.
        )

    @property
    def IVcurve(self):
        """
        Calculate cell I-V curves.
        Returns (Icell, Vcell, Pcell) : tuple of numpy.ndarray of float
        """
        Vdiode = self.Voc * self.pvconst.pts
        VPTS = self.VRBD * self.pvconst.negpts
        Vdiode = np.concatenate((VPTS, Vdiode), axis=0)
        Igen = self.Aph * self.Isc0 * self.Ee
        Idiode1 = self.Isat1 * (np.exp(Vdiode / self.Vt) - 1)
        Idiode2 = self.Isat2 * (np.exp(Vdiode / 2 / self.Vt) - 1)
        Ishunt = Vdiode / self.Rsh
        fRBD = np.asarray(1 - Vdiode / self.VRBD)
        fRBD[fRBD == 0] = np.finfo(np.float64).eps
        fRBD = self.aRBD * fRBD ** (-self.nRBD)
        Icell = Igen - Idiode1 - Idiode2 - Ishunt * (1 + fRBD)
        Vcell = Vdiode - Icell * self.Rs
        Pcell = Icell * Vcell
        return Icell, Vcell, Pcell

    # diode model
    #  *-->--*--->---*--Rs->-Icell--+
    #  ^     |       |              ^
    #  |     |       |              |
    # Igen  Idiode  Ishunt         Vcell
    #  |     |       |              |
    #  |     v       v              v
    #  *--<--*---<---*--<-----------=
    # http://en.wikipedia.org/wiki/Diode_modelling#Shockley_diode_model
    # http://en.wikipedia.org/wiki/Diode#Shockley_diode_equation
    # http://en.wikipedia.org/wiki/William_Shockley

    @staticmethod
    def f_Icell(Icell0, Vcell, Ee, Isc0, Aph, Rs, Vt, Isat1, Isat2, Rsh):
        """
        Objective function for Icell.
        :param Icell0: guess cell current [A]
        :param Vcell: cell voltage [V]
        :param Ee: incident effective irradiance [suns]
        :param Isc0: short circuit current at Tcell and E0 [A]
        :param Aph: photogenerated current coefficient
        :param Rs: series resistance [ohms]
        :param Vt: thermal voltage [V]
        :param Isat1: first diode saturation current at Tcell [A]
        :param Isat2: second diode saturation current [A]
        :param Rsh: shunt resistance [ohms]
        :return: residual = (Icell - Icell0) [A]
        """
        # arbitrary current condition
        Igen = Aph * Ee * Isc0  # photogenerated current
        Vdiode = float(Vcell) + Icell0 * Rs  # diode voltage
        Idiode1 = Isat1 * (np.exp(Vdiode / Vt) - 1.)  # diode current
        Idiode2 = Isat2 * (np.exp(Vdiode / 2. / Vt) - 1.)  # diode current
        Ishunt = Vdiode / Rsh  # shunt current
        return Igen - Idiode1 - Idiode2 - Ishunt - Icell0

    def Icell(self, Vcell):
        """
        Calculate Icell as a function of Vcell.
        :param Vcell: cell voltage [V]
        :return: Icell
        """
        return fsolve(self.f_Icell, 0, (Vcell, self.Ee, self.Isc0, self.Aph,
                      self.Rs, self.Vt, self.Isat1, self.Isat2, self.Rsh))
