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
    i_d = i_sat * factor
    # derivatives
    d__i_sat = factor  # df w.r.t. i_sat
    d__v_d = i_sat * term / denom  # df w.r.t. v_d
    d__m = -i_sat * v_d * term / (m ** 2 * v_t)  # df w.r.t. m
    d__v_t = -i_sat * v_d * term / (m * v_t ** 2)  # df w.r.t. v_t
    jac = np.array([d__i_sat, d__v_d, d__m, d__v_t])  # jacobian
    return i_d, jac


def fish(v_d, r_sh):
    """
    Shunt current, I_sh, and its derivatives w.r.t. v_d and r_sh

    :param v_d: diode voltage [V]
    :param r_sh: shunt resistance [Ohms]
    :return: shunt current
    """
    pass
    # return ish, jish


def fvd(vc, ic, rs):
    """
    Calculates Vd and JVd based on the input parameters
    :param vc: can be an int or a numpy array
    :param ic: can be an int or a numpy array
    :param rs: can be an int or a numpy array
    :return: v_d and jvd both of which are numpy arrays
    Note: If input parameters are numpy arrays, they need to have the same dimensions
    """
    v_d = vc + rs * ic
    if type(v_d) != np.ndarray:
        z = 1
    else:
        z = len(v_d)
    jvd1 = np.ones(z)  # d/dVc
    jvd = np.array([jvd1,
                    rs,  # d/dIc
                    ic])  # d/dRs
    return v_d, jvd