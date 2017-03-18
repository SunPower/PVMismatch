"""
Two diode model methods.
"""

import numpy as np


def fdidv(i_sat1, isat2, rs, rsh, ic, vc, vt):
    """
    Calculates JdIdV and dIdV from the given input parameters.
    :param i_sat1: type can be int or numpy array
    :param isat2: type can be int or numpy array
    :param rs: type can be int or numpy array
    :param rsh: type can be int or numpy array
    :param ic: type can be int or numpy array
    :param vc: type can be int or numpy array
    :param vt: type can be int or numpy array
    :return: didv which is type int or numpy array and jdidv which is type numpy array
    Note: If input parameters are numpy arrays, they need to have the same dimensions
    """
    if type(vt) == int:
        if vt == 0:
            t2 = float("inf")
            t22 = float("inf")
        else:
            t2 = 1. / vt
            t22 = 1. / vt ** 2
    else:
        t2 = 1. / vt
        t22 = 1. / vt ** 2
    if type(rsh) == int:
        if rsh == 0:
            t3 = float("inf")
            t23 = float("inf")
        else:
            t3 = 1. / rsh
            t23 = 1. / rsh ** 2
    else:
        t3 = 1. / rsh
        t23 = 1. / rsh ** 2
    t4 = vc * .5
    t5 = ic * rs * .5
    t6 = t4 + t5
    t7 = t2 * t6
    t8 = np.exp(t7)
    t9 = ic * rs
    t10 = vc + t9
    t11 = t2 * t10
    t12 = np.exp(t11)
    t13 = rs * t3
    t14 = isat2 * rs * t2 * t8 * .5
    t15 = i_sat1 * rs * t2 * t12
    t16 = t13 + t14 + t15 + 1.
    t17 = 1. / t16
    t18 = i_sat1 * t2 * t12
    t19 = isat2 * t2 * t8 * .5
    t20 = t3 + t18 + t19
    didv = -t17 * t20
    t21 = 1. / t16 ** 2
    t24 = rs ** 2
    t25 = isat2 * rs * t8 * t22 * .25
    t26 = i_sat1 * rs * t12 * t22
    t27 = t25 + t26
    jdidv = np.array([-t2 * t12 * t17 + rs * t2 * t12 * t20 * t21,  # d/di_sat1
                      t2 * t8 * t17 * -.5 + rs * t2 * t8 * t20 * t21 * .5,  # d/disat2
                      -t17 * (ic * isat2 * t8 * t22 * .25 + ic * i_sat1 * t12 * t22) + t20 * t21 *
                      (t3 + t18 + t19 + ic * isat2 * rs * t8 * t22 * .25 + ic * i_sat1 * rs * t12 * t22),  # d/drs
                      t17 * t23 - rs * t20 * t21 * t23,  # d/drsh
                      -t17 * t27 + t20 * t21 * (isat2 * t8 * t22 * t24 * .25 + i_sat1 * t12 * t22 * t24),  # d/dic
                      -t17 * (isat2 * t8 * t22 * .25 + i_sat1 * t12 * t22) + t20 * t21 * t27])  # d/dvc
    return didv, jdidv


def fdpdv(i_sat1, isat2, rs, rsh, ic, vc, vt):
    """
    Calculates JdPdV and dPdV from the given input parameters.
    :param i_sat1: type can be int or numpy array
    :param isat2: type can be int or numpy array
    :param rs: type can be int or numpy array
    :param rsh: type can be int or numpy array
    :param ic: type can be int or numpy array
    :param vc: type can be int or numpy array
    :param vt: type can be int or numpy array
    :return: dpdv which is type int or numpy array and jdpdv which is type numpy array
    Note: If input parameters are numpy arrays, they need to have the same dimensions
    """
    if type(vt) == int:
        if vt == 0:
            t2 = float("inf")
            t22 = float("inf")
        else:
            t2 = 1. / vt
            t22 = 1. / vt ** 2
    else:
        t2 = 1. / vt
        t22 = 1. / vt ** 2
    if type(rsh) == int:
        if rsh == 0:
            t3 = float("inf")
            t23 = float("inf")
        else:
            t3 = 1. / rsh
            t23 = 1. / rsh ** 2
    else:
        t3 = 1. / rsh
        t23 = 1. / rsh ** 2
    t4 = vc * .5
    t5 = ic * rs * .5
    t6 = t4 + t5
    t7 = t2 * t6
    t8 = np.exp(t7)
    t9 = ic * rs
    t10 = vc + t9
    t11 = t2 * t10
    t12 = np.exp(t11)
    t13 = rs * t3
    t14 = isat2 * rs * t2 * t8 * .5
    t15 = i_sat1 * rs * t2 * t12
    t16 = t13 + t14 + t15 + 1.
    t17 = 1. / t16
    t18 = i_sat1 * t2 * t12
    t19 = isat2 * t2 * t8 * .5
    t20 = t3 + t18 + t19
    dpdv = ic - vc * t17 * t20
    t21 = 1. / t16 ** 2
    t24 = rs ** 2
    t25 = isat2 * rs * t8 * t22 * .25
    t26 = i_sat1 * rs * t12 * t22
    t27 = t25 + t26
    jdpdv = np.array([-vc * t2 * t12 * t17 + rs * vc * t2 * t12 * t20 * t21,  # d/di_sat1
                      vc * t2 * t8 * t17 * -.5 + rs * vc * t2 * t8 * t20 * t21 * .5,  # d/disat2
                      -vc * t17 * (ic * isat2 * t8 * t22 * .25 + ic * i_sat1 * t12 * t22) + vc * t20 * t21 *
                      (t3 + t18 + t19 + ic * isat2 * rs * t8 * t22 * .25 + ic * i_sat1 * rs * t12 * t22),  # d/drs
                      vc * t17 * t23 - rs * vc * t20 * t21 * t23,  # d/drsh
                      -vc * t17 * t27 + vc * t20 * t21 * (isat2 * t8 * t22 * t24 *
                                                          .25 + i_sat1 * t12 * t22 * t24) + 1.,  # d/dic
                      -t17 * t20 - vc * t17 * (isat2 * t8 * t22 * .25 + i_sat1 * t12 * t22) + vc * t20 *
                      t21 * t27])  # d/dvc
    return dpdv, jdpdv


def fjrsh(i_sat1, isat2, rs, rsh, vt, isco):
    """
    Calculates FRsh and JRsh from the given input parameters.
    :param i_sat1: type can be int or numpy array
    :param isat2: type can be int or numpy array
    :param rs: type can be int or numpy array
    :param rsh: type can be int or numpy array
    :param vt: type can be int or numpy array
    :param isco: type can be int or numpy array
    :return: frsh which is type int or numpy array and jrsh which is type numpy array
    Note: If input parameters are numpy arrays, they need to have the same dimensions
    """
    if type(vt) == int:
        if vt == 0:
            t2 = float("inf")
            t17 = float("inf")
        else:
            t2 = 1. / vt
            t17 = 1. / vt ** 2
    else:
        t2 = 1. / vt
        t17 = 1. / vt ** 2
    if type(rsh) == int:
        if rsh == 0:
            t3 = float("inf")
            t18 = float("inf")
        else:
            t3 = 1. / rsh
            t18 = 1. / rsh ** 2
    else:
        t3 = 1. / rsh
        t18 = 1. / rsh ** 2
    t4 = isco * rs * t2
    t5 = np.exp(t4)
    t6 = isco * rs * t2 * .5
    t7 = np.exp(t6)
    t8 = i_sat1 * t2 * t5
    t9 = isat2 * t2 * t7 * .5
    t10 = t3 + t8 + t9
    t11 = 1. / t10
    t12 = rs * t3
    t13 = i_sat1 * rs * t2 * t5
    t14 = isat2 * rs * t2 * t7 * .5
    t15 = t12 + t13 + t14 + 1.
    frsh = rsh - t11 * t15
    t16 = 1. / t10 ** 2
    jrsh = np.array([-rs * t2 * t5 * t11 + t2 * t5 * t15 * t16,  # d/di_sat1
                     rs * t2 * t7 * t11 * -.5 + t2 * t7 * t15 * t16 * .5,  # d/disat2
                     -t11 * (t3 + t8 + t9 + i_sat1 * isco * rs * t5 * t17 + isat2 * isco * rs * t7 * t17 * .25) + t15 *
                     t16 * (i_sat1 * isco * t5 * t17 + isat2 * isco * t7 * t17 * .25),  # d/drs
                     rs * t11 * t18 - t15 * t16 * t18 + 1.])  # d/drsh
    return frsh, jrsh