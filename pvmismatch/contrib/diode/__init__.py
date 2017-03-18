import numpy as np


def fid(i_sat, v_d, m, v_t):
    """
    Diode current, I_d, and its derivatives w.r.t. I_sat, V_d, m and V_t.

    :param i_sat: diode saturation current [A]
    :type i_sat: float
    :param v_d: diode voltage [V]
    :type v_d: float
    :param m: diode ideality factor
    :type m: float
    :param v_t: thermal voltage [V]
    :type v_t: float
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
    denom = m * v_t
    term = np.exp(v_d / denom)
    factor = (term - 1.0)
    # diode current
    i_d = np.atleast_1d(i_sat * factor)
    # derivatives
    d__i_sat = np.atleast_1d(factor)  # df w.r.t. i_sat
    d__v_d = np.atleast_1d(i_sat * term / denom)  # df w.r.t. v_d
    d__m = np.atleast_1d(-i_sat * v_d * term / (m ** 2 * v_t))  # df w.r.t. m
    d__v_t = np.atleast_1d(-i_sat * v_d * term / (m * v_t ** 2))  # df w.r.t. v_t
    jac = np.array([d__i_sat, d__v_d, d__m, d__v_t])  # jacobian
    return i_d, jac


def fish(v_d, r_sh):
    """
    Shunt current, I_sh, and its derivatives w.r.t. V_d and R_sh.

    :param v_d: diode voltage [V]
    :param r_sh: shunt resistance [Ohms]
    :return: shunt current [A]
    """
    i_sh = np.atleast_1d(v_d / r_sh)
    d__v_d = np.atleast_1d(1.0 / r_sh)
    d__r_sh = np.atleast_1d(-i_sh * d__v_d)
    jac = np.array([d__v_d, d__r_sh])
    return i_sh, jac


def fvd(v_c, i_c, r_s):
    """
    Diode voltage, V_d, and its derivatives w.r.t. V_c, I_c, R_s.

    :param v_c: cell voltage [V]
    :param i_c: cell current [A]
    :param r_s: series resistance [Ohms]
    :return: diode voltage [V]
    """
    v_d = np.atleast_1d(v_c + r_s * i_c)
    jac = np.array([np.ones(v_d.shape),
                    np.atleast_1d(r_s),  # d/dIc
                    np.atleast_1d(i_c)])  # d/dRs
    return v_d, jac
