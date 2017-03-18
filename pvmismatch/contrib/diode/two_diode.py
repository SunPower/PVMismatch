"""
Two diode model methods.
"""

import numpy as np


def fdidv(i_sat1, i_sat2, r_s, r_sh, i_c, v_c, v_t):
    """
    Calculates JdIdV and dIdV from the given input parameters.
    :param i_sat1: type can be int or numpy array
    :param i_sat2: type can be int or numpy array
    :param r_s: type can be int or numpy array
    :param r_sh: type can be int or numpy array
    :param i_c: type can be int or numpy array
    :param v_c: type can be int or numpy array
    :param v_t: type can be int or numpy array
    :return: didv which is type int or numpy array and jdidv which is type numpy array
    Note: If input parameters are numpy arrays, they need to have the same dimensions
    """
    v_d = v_c + i_c * r_s
    quotient = v_d / v_t
    v_sat1_sh, v_sat2_sh = i_sat1 * r_sh, i_sat2 * r_sh
    didv = (-(v_sat1_sh * np.exp(quotient)
              + 0.5 * v_sat2_sh * np.exp(0.5 * quotient) + v_t)
            / (v_sat1_sh * r_s * np.exp(quotient)
               + 0.5 * v_sat2_sh * r_s * np.exp(0.5 * quotient)
               + r_s * v_t + r_sh * v_t))
    didv__i_sat1 = (
        r_s * r_sh * (
            v_sat1_sh * np.exp(quotient)
            + 0.5 * v_sat2_sh * np.exp(0.5 * quotient) + v_t
        ) * np.exp(quotient)
        / (v_sat1_sh * r_s * np.exp(quotient)
           + 0.5 * v_sat2_sh * r_s * np.exp(0.5 * quotient)
           + r_s * v_t + r_sh * v_t)**2.0 - 2.0 * r_sh * np.exp(quotient)
        / (v_sat1_sh * r_s * np.exp(quotient)
           + 0.5 * v_sat2_sh * r_s * np.exp(0.5 * quotient)
           + r_s * v_t + r_sh * v_t)
    )
    jac = np.array([didv__i_sat1])
    return didv, jac


def fdpdv(i_sat1, i_sat2, r_s, r_sh, i_c, v_c, v_t):
    """
    Calculates JdPdV and dPdV from the given input parameters.
    :param i_sat1: type can be int or numpy array
    :param i_sat2: type can be int or numpy array
    :param r_s: type can be int or numpy array
    :param r_sh: type can be int or numpy array
    :param i_c: type can be int or numpy array
    :param v_c: type can be int or numpy array
    :param v_t: type can be int or numpy array
    :return: dpdv which is type int or numpy array and jdpdv which is type numpy array
    Note: If input parameters are numpy arrays, they need to have the same dimensions
    """
    if type(v_t) == int:
        if v_t == 0:
            t2 = float("inf")
            t22 = float("inf")
        else:
            t2 = 1. / v_t
            t22 = 1. / v_t ** 2
    else:
        t2 = 1. / v_t
        t22 = 1. / v_t ** 2
    if type(r_sh) == int:
        if r_sh == 0:
            t3 = float("inf")
            t23 = float("inf")
        else:
            t3 = 1. / r_sh
            t23 = 1. / r_sh ** 2
    else:
        t3 = 1. / r_sh
        t23 = 1. / r_sh ** 2
    t4 = v_c * .5
    t5 = i_c * r_s * .5
    t6 = t4 + t5
    t7 = t2 * t6
    t8 = np.exp(t7)
    t9 = i_c * r_s
    t10 = v_c + t9
    t11 = t2 * t10
    t12 = np.exp(t11)
    t13 = r_s * t3
    t14 = i_sat2 * r_s * t2 * t8 * .5
    t15 = i_sat1 * r_s * t2 * t12
    t16 = t13 + t14 + t15 + 1.
    t17 = 1. / t16
    t18 = i_sat1 * t2 * t12
    t19 = i_sat2 * t2 * t8 * .5
    t20 = t3 + t18 + t19
    dpdv = i_c - v_c * t17 * t20
    t21 = 1. / t16 ** 2
    t24 = r_s ** 2
    t25 = i_sat2 * r_s * t8 * t22 * .25
    t26 = i_sat1 * r_s * t12 * t22
    t27 = t25 + t26
    jdpdv = np.array([-v_c * t2 * t12 * t17 + r_s * v_c * t2 * t12 * t20 * t21,  # d/di_sat1
                      v_c * t2 * t8 * t17 * -.5 + r_s * v_c * t2 * t8 * t20 * t21 * .5,  # d/disat2
                      -v_c * t17 * (i_c * i_sat2 * t8 * t22 * .25 + i_c * i_sat1 * t12 * t22) + v_c * t20 * t21 *
                      (t3 + t18 + t19 + i_c * i_sat2 * r_s * t8 * t22 * .25 + i_c * i_sat1 * r_s * t12 * t22),  # d/drs
                      v_c * t17 * t23 - r_s * v_c * t20 * t21 * t23,  # d/drsh
                      -v_c * t17 * t27 + v_c * t20 * t21 * (i_sat2 * t8 * t22 * t24 *
                                                          .25 + i_sat1 * t12 * t22 * t24) + 1.,  # d/dic
                      -t17 * t20 - v_c * t17 * (i_sat2 * t8 * t22 * .25 + i_sat1 * t12 * t22) + v_c * t20 *
                      t21 * t27])  # d/dvc
    return dpdv, jdpdv


def fjrsh(i_sat1, i_sat2, r_s, r_sh, v_t, isco):
    """
    Calculates FRsh and JRsh from the given input parameters.
    :param i_sat1: type can be int or numpy array
    :param i_sat2: type can be int or numpy array
    :param r_s: type can be int or numpy array
    :param r_sh: type can be int or numpy array
    :param v_t: type can be int or numpy array
    :param isco: type can be int or numpy array
    :return: frsh which is type int or numpy array and jrsh which is type numpy array
    Note: If input parameters are numpy arrays, they need to have the same dimensions
    """
    if type(v_t) == int:
        if v_t == 0:
            t2 = float("inf")
            t17 = float("inf")
        else:
            t2 = 1. / v_t
            t17 = 1. / v_t ** 2
    else:
        t2 = 1. / v_t
        t17 = 1. / v_t ** 2
    if type(r_sh) == int:
        if r_sh == 0:
            t3 = float("inf")
            t18 = float("inf")
        else:
            t3 = 1. / r_sh
            t18 = 1. / r_sh ** 2
    else:
        t3 = 1. / r_sh
        t18 = 1. / r_sh ** 2
    t4 = isco * r_s * t2
    t5 = np.exp(t4)
    t6 = isco * r_s * t2 * .5
    t7 = np.exp(t6)
    t8 = i_sat1 * t2 * t5
    t9 = i_sat2 * t2 * t7 * .5
    t10 = t3 + t8 + t9
    t11 = 1. / t10
    t12 = r_s * t3
    t13 = i_sat1 * r_s * t2 * t5
    t14 = i_sat2 * r_s * t2 * t7 * .5
    t15 = t12 + t13 + t14 + 1.
    frsh = r_sh - t11 * t15
    t16 = 1. / t10 ** 2
    jrsh = np.array([-r_s * t2 * t5 * t11 + t2 * t5 * t15 * t16,  # d/di_sat1
                     r_s * t2 * t7 * t11 * -.5 + t2 * t7 * t15 * t16 * .5,  # d/disat2
                     -t11 * (t3 + t8 + t9 + i_sat1 * isco * r_s * t5 * t17 + i_sat2 * isco * r_s * t7 * t17 * .25) + t15 *
                     t16 * (i_sat1 * isco * t5 * t17 + i_sat2 * isco * t7 * t17 * .25),  # d/drs
                     r_s * t11 * t18 - t15 * t16 * t18 + 1.])  # d/drsh
    return frsh, jrsh