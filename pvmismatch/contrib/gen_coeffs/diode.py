"""
Common diode model equations.
"""

import numpy as np
from scipy.constants import elementary_charge as QE, Boltzmann as KB

T0 = 25.0  # [C]
E0 = 1000.0  # [W/m^2]
EG = 1.1  # [eV]]


def fid(isat, vd, m, vt):
    """
    Diode current, I_d, and its derivatives w.r.t. I_sat, V_d, m and V_t.

    :param isat: diode saturation current [A]
    :type isat: float
    :param vd: diode voltage [V]
    :type vd: float
    :param m: diode ideality factor
    :type m: float
    :param vt: thermal voltage [V]
    :type vt: float
    :return: diode current [A] and its derivatives
    :rtype: float

    Diode current is given by Shockley's equation ...

    .. math::
        I_d = I_{sat} \\left(\\exp\\left(\\frac{V_d}{m V_t} \\right) - 1\\right)

    ... where I_d is the diode current in amps, I_sat is the saturation current
    in amps, V_d is the diode voltage in volts, m is the diode ideality factor
    and V_t is the thermal voltage in volts ...

    .. math::
        V_t = \\frac{k_B T}{q_e}

    ... in which k_B is the Boltzmann constant, T is the ambient temperature in
    Kelvin and q_e is teh elementary charge in coulombs per electron.

    https://en.wikipedia.org/wiki/Shockley_diode_equation

    """
    vact = m * vt  # activation voltage [V]
    growth = np.exp(vd / vact)  # growth term
    expfact = (growth - 1.0)  # exponential factor
    isat_growth = isat * growth  # combination parameter
    vd_isat_growth = -vd * isat_growth  # combination parameter
    # diode current
    id_ = np.atleast_1d(isat * expfact)
    # derivatives
    d_isat = np.atleast_1d(expfact)  # df w.r.t. isat
    d_vd = np.atleast_1d(isat_growth / vact)  # df w.r.t. vd
    d_m = np.atleast_1d(vd_isat_growth / (m ** 2.0 * vt))  # df w.r.t. m
    d_vt = np.atleast_1d(vd_isat_growth / (m * vt ** 2.0))  # df w.r.t. vt
    jac = np.array([d_isat, d_vd, d_m, d_vt])  # jacobian
    return id_, jac


def fish(vd, rsh):
    """
    Shunt current, I_sh, and its derivatives w.r.t. V_d and R_sh.

    :param vd: diode voltage [V]
    :param rsh: shunt resistance [Ohms]
    :return: shunt current [A]
    """
    ish = np.atleast_1d(vd / rsh)
    shaper = np.ones(ish.shape)  # make sure scalars are the right shape
    d_vd = np.atleast_1d(1.0 / rsh) * shaper
    d_rsh = np.atleast_1d(-ish * d_vd)
    jac = np.array([d_vd, d_rsh])
    return ish, jac


def fvd(vc, ic, rs):
    """
    Diode voltage, V_d, and its derivatives w.r.t. V_c, I_c, R_s.

    :param vc: cell voltage [V]
    :param ic: cell current [A]
    :param rs: series resistance [Ohms]
    :return: diode voltage [V]
    """
    vd = np.atleast_1d(vc + rs * ic)
    shaper = np.ones(vd.shape)  # make sure scalars are the right shape
    jac = np.array([np.ones(vd.shape),
                    np.atleast_1d(rs) * shaper,  # d/dIc
                    np.atleast_1d(ic) * shaper])  # d/dRs
    return vd, jac


def isat_t(tc, isat0):
    tck = tc + 273.15
    t0k = T0 + 273.15
    tstar = tck ** 3.0 / t0k ** 3.0
    inv_delta_t = 1.0 / t0k - 1.0 / tck  # [1/K]
    exp_tstar = np.exp(EG * QE / KB * inv_delta_t)
    isat_t = isat0 * tstar * exp_tstar
    return isat_t


def isc_t(tc, isc0, alpha_isc):
    delta_t = tc - T0
    isc_t = isc0 * (1.0 + alpha_isc * delta_t)
    return isc_t


def aph(tc, isc0, alpha_isc, isat1, isat2, vt, rs, rsh):
    isc = isc_t(tc, isc0, alpha_isc)
    vd_sc, _ = fvd(0, isc, rs)
    isat1_t = isat_t(tc, isat0=isat1)
    id1_sc, _ = fid(isat1_t, vd_sc, 1.0, vt)
    id2_sc, _ = fid(isat2, vd_sc, 2.0, vt)
    ish_sc, _ = fish(vd_sc, rsh)
    aph = 1.0 + (id1_sc + id2_sc + ish_sc) / isc
    return aph
