"""
Two diode model methods.
"""

import numpy as np


def fdidv(isat1, isat2, rs, rsh, ic, vc, vt):
    """
    Calculates JdIdV and dIdV from the given input parameters.
    :param isat1: type can be int or numpy array
    :param isat2: type can be int or numpy array
    :param rs: type can be int or numpy array
    :param rsh: type can be int or numpy array
    :param ic: type can be int or numpy array
    :param vc: type can be int or numpy array
    :param vt: type can be int or numpy array
    :return: didv which is type int or numpy array and jdidv which is type numpy array
    Note: If input parameters are numpy arrays, they need to have the same dimensions
    """
    v_d = vc + ic * rs
    vstar = v_d / vt
    rstar = rsh / rs
    exp_vstar, exp_vstar_2 = np.exp(vstar), np.exp(0.5 * vstar)
    v_sat1_sh, v_sat2_sh = isat1 * rsh, isat2 * rsh
    v_sat1_sh_exp_vstar = v_sat1_sh * exp_vstar
    v_sat2_sh_exp_vstar_2 = 0.5 * v_sat2_sh * exp_vstar_2
    didv = (
        -1.0 / rs * (v_sat1_sh_exp_vstar + v_sat2_sh_exp_vstar_2 + vt)
        / (v_sat1_sh_exp_vstar + v_sat2_sh_exp_vstar_2 + vt * (1.0 + rstar))
    )
    didv__i_sat1 = (
        rstar * exp_vstar * (
            v_sat1_sh_exp_vstar + v_sat2_sh_exp_vstar_2 + vt
        ) / (
            v_sat1_sh_exp_vstar + v_sat2_sh_exp_vstar_2 + vt * (1.0 + rstar)
        )**2.0 - rstar * exp_vstar / (
            v_sat1_sh_exp_vstar + v_sat2_sh_exp_vstar_2 + vt * (1.0 + rstar)
        )
    )
    didv__i_sat2 = (
        0.5*rstar*exp_vstar_2*(
            v_sat1_sh_exp_vstar + v_sat2_sh_exp_vstar_2 + vt
        )/(
            v_sat1_sh_exp_vstar + v_sat2_sh_exp_vstar_2 + vt*(1.0 + rstar)
        )**2.0 - 0.5*rstar*exp_vstar_2/(
            v_sat1_sh_exp_vstar + v_sat2_sh_exp_vstar_2 + vt*(1.0 + rstar)
        )
    )
    didv__r_s = (
        -(
            v_sat1_sh*ic*exp_vstar/vt + 0.25*v_sat2_sh*ic*exp_vstar_2/vt
        )/(
            v_sat1_sh*rs*exp_vstar + 0.5*v_sat2_sh*rs*exp_vstar_2
            + rs*vt + rsh*vt
        ) - (
            v_sat1_sh_exp_vstar + v_sat2_sh_exp_vstar_2 + vt
        )*(
            -v_sat1_sh*rs*ic*exp_vstar/vt
            - v_sat1_sh_exp_vstar
            - 0.25*v_sat2_sh*rs*ic*exp_vstar_2/vt
            - v_sat2_sh_exp_vstar_2 - vt
        )/(
            v_sat1_sh*rs*exp_vstar + 0.5*v_sat2_sh*rs*exp_vstar_2
            + rs*vt + rsh*vt
        )**2.0
    )

    didv__r_sh = (
        -(
            2.0*isat1*exp_vstar + isat2*exp_vstar_2
        )/(
            2.0*v_sat1_sh*rs*exp_vstar + v_sat2_sh*rs*exp_vstar_2
            + 2.0*rs*vt + 2.0*rsh*vt
        ) - (
            -2.0*isat1*rs*exp_vstar - isat2*rs*exp_vstar_2
            - 2.0*vt
        )*(
            2.0*v_sat1_sh_exp_vstar + v_sat2_sh*exp_vstar_2 + 2.0*vt
        )/(
            2.0*v_sat1_sh*rs*exp_vstar + v_sat2_sh*rs*exp_vstar_2
            + 2.0*rs*vt + 2.0*rsh*vt
        )**2
    )
    didv__i_c = (
        -(
            2.0*v_sat1_sh*rs*exp_vstar/vt
            + 0.5*v_sat2_sh*rs*exp_vstar_2/vt
        )/(
            2.0*v_sat1_sh*rs*exp_vstar + v_sat2_sh*rs*exp_vstar_2
            + 2.0*rs*vt + 2.0*rsh*vt
        ) - (
            -2.0*isat1*rs**2*rsh*exp_vstar/vt
            - 0.5*isat2*rs**2*rsh*exp_vstar_2/vt
        )*(
            2.0*v_sat1_sh_exp_vstar + v_sat2_sh*exp_vstar_2 + 2.0*vt
        )/(
            2.0*v_sat1_sh*rs*exp_vstar + v_sat2_sh*rs*exp_vstar_2
            + 2.0*rs*vt + 2.0*rsh*vt
        )**2
    )
    didv__v_c = (
        -(
            2.0*v_sat1_sh*(rs*didv + 1)*exp_vstar/vt
            + 0.5*v_sat2_sh*(rs*didv + 1)*exp_vstar_2/vt
        )/(
            2.0*v_sat1_sh*rs*exp_vstar + v_sat2_sh*rs*exp_vstar_2
            + 2.0*rs*vt + 2.0*rsh*vt
        ) - (
            -2.0*v_sat1_sh*rs*(rs*didv + 1)*exp_vstar/vt
            - 0.5*v_sat2_sh*rs*(rs*didv + 1)*exp_vstar_2/vt
        )*(
            2.0*v_sat1_sh_exp_vstar + v_sat2_sh*exp_vstar_2 + 2.0*vt
        )/(
            2.0*v_sat1_sh*rs*exp_vstar + v_sat2_sh*rs*exp_vstar_2
            + 2.0*rs*vt + 2.0*rsh*vt
        )**2
    )
    jac = np.array([
        didv__i_sat1, didv__i_sat2, didv__r_s, didv__r_sh, didv__i_c, didv__v_c
    ])
    return didv, jac


def fdpdv(isat1, isat2, rs, rsh, ic, vc, vt):
    """
    Calculates JdPdV and dPdV from the given input parameters.
    :param isat1: type can be int or numpy array
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
    t15 = isat1 * rs * t2 * t12
    t16 = t13 + t14 + t15 + 1.
    t17 = 1. / t16
    t18 = isat1 * t2 * t12
    t19 = isat2 * t2 * t8 * .5
    t20 = t3 + t18 + t19
    dpdv = ic - vc * t17 * t20
    t21 = 1. / t16 ** 2
    t24 = rs ** 2
    t25 = isat2 * rs * t8 * t22 * .25
    t26 = isat1 * rs * t12 * t22
    t27 = t25 + t26
    jdpdv = np.array([-vc * t2 * t12 * t17 + rs * vc * t2 * t12 * t20 * t21,  # d/di_sat1
                      vc * t2 * t8 * t17 * -.5 + rs * vc * t2 * t8 * t20 * t21 * .5,  # d/disat2
                      -vc * t17 * (ic * isat2 * t8 * t22 * .25 + ic * isat1 * t12 * t22) + vc * t20 * t21 *
                      (t3 + t18 + t19 + ic * isat2 * rs * t8 * t22 * .25 + ic * isat1 * rs * t12 * t22),  # d/drs
                      vc * t17 * t23 - rs * vc * t20 * t21 * t23,  # d/drsh
                      -vc * t17 * t27 + vc * t20 * t21 * (isat2 * t8 * t22 * t24 *
                                                          .25 + isat1 * t12 * t22 * t24) + 1.,  # d/dic
                      -t17 * t20 - vc * t17 * (isat2 * t8 * t22 * .25 + isat1 * t12 * t22) + vc * t20 *
                      t21 * t27])  # d/dvc
    return dpdv, jdpdv


def fjrsh(isat1, isat2, rs, rsh, vt, isco):
    """
    Calculates FRsh and JRsh from the given input parameters.
    :param isat1: type can be int or numpy array
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
    t8 = isat1 * t2 * t5
    t9 = isat2 * t2 * t7 * .5
    t10 = t3 + t8 + t9
    t11 = 1. / t10
    t12 = rs * t3
    t13 = isat1 * rs * t2 * t5
    t14 = isat2 * rs * t2 * t7 * .5
    t15 = t12 + t13 + t14 + 1.
    frsh = rsh - t11 * t15
    t16 = 1. / t10 ** 2
    jrsh = np.array([-rs * t2 * t5 * t11 + t2 * t5 * t15 * t16,  # d/di_sat1
                     rs * t2 * t7 * t11 * -.5 + t2 * t7 * t15 * t16 * .5,  # d/disat2
                     -t11 * (t3 + t8 + t9 + isat1 * isco * rs * t5 * t17 + isat2 * isco * rs * t7 * t17 * .25) + t15 *
                     t16 * (isat1 * isco * t5 * t17 + isat2 * isco * t7 * t17 * .25),  # d/drs
                     rs * t11 * t18 - t15 * t16 * t18 + 1.])  # d/drsh
    return frsh, jrsh