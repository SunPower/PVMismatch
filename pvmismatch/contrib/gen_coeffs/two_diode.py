"""
Two diode model equations.
"""

import numpy as np
from pvmismatch.contrib.gen_coeffs import diode


def fdidv(isat1, isat2, rs, rsh, ic, vc, vt):
    """
    Derivative of IV curve and its derivatives w.r.t. Isat1, Isat2, Rs, Rsh, Ic,
    Vc and Vt.

    :param isat1: diode 1 saturation current [A]
    :param isat2: diode 2 saturation current [A]
    :param rs: series resistance [ohms]
    :param rsh: shunt resistance [ohms]
    :param ic: cell current [A]
    :param vc: cell voltage [V]
    :param vt: thermal voltage (kB * Tc / qe = 26[mV] at Tc=298K) [V]
    :return: derivative of IV curve and its derivatives
    """
    vd, _ = diode.fvd(vc, ic, rs)  # vd = vc + ic * rs
    vstar = vd / vt
    rstar = rsh / rs
    exp_vstar, exp_vstar_2 = np.exp(vstar), np.exp(0.5 * vstar)
    v_sat1_sh, v_sat2_sh = isat1 * rsh, isat2 * rsh
    v_sat1_sh_exp_vstar = v_sat1_sh * exp_vstar
    v_sat2_sh_exp_vstar_2 = 0.5 * v_sat2_sh * exp_vstar_2
    vsum = v_sat1_sh_exp_vstar + v_sat2_sh_exp_vstar_2 + vt
    vsum_rstar = vsum + vt * rstar
    combiterm1 = v_sat1_sh_exp_vstar + 0.5*v_sat2_sh_exp_vstar_2
    combiterm2 = isat1*exp_vstar + 0.5*isat2*exp_vstar_2
    combiterm3 = vsum / vsum_rstar - 1.0
    combiterm4 = vsum_rstar * rs
    combiterm5 = rstar * combiterm3 / vsum_rstar
    combiterm6 = combiterm1 * combiterm3 / vt
    combiterm7 = 1.0 / combiterm4
    # dI/dV = derivative of IV curve
    didv = -vsum / combiterm4
    # jacobian
    didv_isat1 = exp_vstar * combiterm5
    didv_isat2 = 0.5 * exp_vstar_2 * combiterm5
    didv__r_s = combiterm7 * (combiterm6 * ic + vsum**2.0 / combiterm4)
    didv_rsh = combiterm7 * (combiterm2 * combiterm3 + vt * vsum / combiterm4)
    didv_ic = combiterm6 / vsum_rstar
    didv_vc = (didv + 1.0 / rs) * didv_ic
    jac = np.array([
        didv_isat1, didv_isat2, didv__r_s, didv_rsh, didv_ic, didv_vc
    ])
    return didv, jac


def fdpdv(isat1, isat2, rs, rsh, ic, vc, vt):
    """
    Derivative of PV curve and its derivatives w.r.t. Isat1, Isat2, Rs, Rsh, Ic,
    Vc and Vt.

    :param isat1: diode 1 saturation current [A]
    :param isat2: diode 2 saturation current [A]
    :param rs: series resistance [ohms]
    :param rsh: shunt resistance [ohms]
    :param ic: cell current [A]
    :param vc: cell voltage [V]
    :param vt: thermal voltage (kB * Tc / qe = 26[mV] at Tc=298K) [V]
    :return: derivative of PV curve and its derivatives
    """
    didv, _ = fdidv(isat1, isat2, rs, rsh, ic, vc, vt)
    vd, _ = diode.fvd(vc, ic, rs)  # vd = vc + ic * rs
    dpdv = didv * vc + ic
    dpdv_isat1 = 2.0*rs*rsh*vc*(
        2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt
    )*np.exp(vd/vt)/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    )**2 - 2.0*rsh*vc*np.exp(vd/vt)/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    )
    dpdv_isat2 = rs*rsh*vc*(
        2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt
    )*np.exp(0.5*vd/vt)/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    )**2 - rsh*vc*np.exp(0.5*vd/vt)/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    )
    dpdv_rs = -vc*(
        2.0*isat1*rsh*ic*np.exp(vd/vt)/vt
        + 0.5*isat2*rsh*ic*np.exp(0.5*vd/vt)/vt
    )/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    ) - vc*(
        2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt
    )*(
        -2.0*isat1*rs*rsh*ic*np.exp(vd/vt)/vt
        - 2.0*isat1*rsh*np.exp(vd/vt)
        - 0.5*isat2*rs*rsh*ic*np.exp(0.5*vd/vt)/vt
        - isat2*rsh*np.exp(0.5*vd/vt) - 2.0*vt
    )/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    )**2
    dpdv_rsh = -vc*(
        2.0*isat1*np.exp(vd/vt) + isat2*np.exp(0.5*vd/vt)
    )/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    ) - vc*(
        -2.0*isat1*rs*np.exp(vd/vt) - isat2*rs*np.exp(0.5*vd/vt) - 2.0*vt
    )*(
        2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt
    )/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    )**2
    dpdv_ic = -vc*(
        2.0*isat1*rs*rsh*np.exp(vd/vt)/vt
        + 0.5*isat2*rs*rsh*np.exp(0.5*vd/vt)/vt
    )/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    ) - vc*(
        -2.0*isat1*rs**2*rsh*np.exp(vd/vt)/vt
        - 0.5*isat2*rs**2*rsh*np.exp(0.5*vd/vt)/vt
    )*(
        2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt
    )/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    )**2 + 1.0
    dpdv_vc = -vc*(
        2.0*isat1*rsh*(rs*didv + 1)*np.exp(vd/vt)/vt
        + 0.5*isat2*rsh*(rs*didv + 1)*np.exp(0.5*vd/vt)/vt
    )/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    ) - vc*(
        -2.0*isat1*rs*rsh*(rs*didv + 1)*np.exp(vd/vt)/vt
        - 0.5*isat2*rs*rsh*(rs*didv + 1)*np.exp(0.5*vd/vt)/vt
    )*(
        2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt
    )/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    )**2 - (
        2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt
    )/(
        2.0*isat1*rs*rsh*np.exp(vd/vt)
        + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
    ) + didv
    jac = np.array([
        dpdv_isat1, dpdv_isat2, dpdv_rs, dpdv_rsh, dpdv_ic, dpdv_vc
        ])
    return dpdv, jac


def fjrsh(isat1, isat2, rs, rsh, vt, isc):
    """
    Shunt resistance residual and its derivatives w.r.t. Isat1, Isat2, Rs and
    Rsh.

    :param isat1: diode 1 saturation current [A]
    :param isat2: diode 2 saturation current [A]
    :param rs: series resistance [ohms]
    :param rsh: shunt resistance [ohms]
    :param vt: thermal voltage (kB * Tc / qe = 26[mV] at Tc=298K) [V]
    :param isc: short circuit current [A]
    :return: Rsh residual and its derivatives

    Shunt resistance is assumed to be equal to the inverse of the slope of the
    IV curve at short circuit.

    .. math::
        Rsh = \\frac{ -1 }{ \\left. \\frac{dI}{dV} \\right|_{V=0} }

    This assumption is valid when [put condition here].
    """
    didv, _ = fdidv(isat1, isat2, rs, rsh, ic=isc, vc=0, vt=vt)
    vd, _ = diode.fvd(0.0, isc, rs)  # vd = vc + ic * rs = 0.0 + isc * rs
    # frsh = rsh + 1/didv
    frsh = vd * (1.0/rsh + didv)
    dfrsh_isat1 = vd*(
        2.0*rs*rsh*(
            2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt
        )*np.exp(vd/vt)/(
            2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt)
            + 2.0*rs*vt + 2.0*rsh*vt
        )**2 - 2.0*rsh*np.exp(vd/vt)/(
            2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt)
            + 2.0*rs*vt + 2.0*rsh*vt
        )
    )
    dfrsh_isat2 = vd*(
        rs*rsh*(
            2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt
        )*np.exp(0.5*vd/vt)/(
            2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt)
            + 2.0*rs*vt + 2.0*rsh*vt
        )**2 - rsh*np.exp(0.5*vd/vt)/(
            2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt)
            + 2.0*rs*vt + 2.0*rsh*vt
        )
    )
    dfrsh_rs = (
        vd*(
            -(
                2.0*isat1*rsh*isc*np.exp(vd/vt)/vt + 0.5*isat2*rsh*isc*np.exp(0.5*vd/vt)/vt
            )/(
                2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
            ) - (
                2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt
            )*(
                -2.0*isat1*rs*rsh*isc*np.exp(vd/vt)/vt
                - 2.0*isat1*rsh*np.exp(vd/vt)
                - 0.5*isat2*rs*rsh*isc*np.exp(0.5*vd/vt)/vt
                - isat2*rsh*np.exp(0.5*vd/vt) - 2.0*vt
            )/(
                2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
            )**2
        ) + (
            -(2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt)/(
                2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
            ) + 1.0/rsh
        )*isc
    )
    dfrsh_rsh = (
        vd*(
            -(2.0*isat1*np.exp(vd/vt) + isat2*np.exp(0.5*vd/vt))/(
                2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
            ) - (
                -2.0*isat1*rs*np.exp(vd/vt) - isat2*rs*np.exp(0.5*vd/vt) - 2.0*vt
            )*(2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt)/(
                2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
            )**2 - 1.0/rsh**2
        )
    )
    dfrsh_ic = (
        rs*(
            -(2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt)/(
                2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
            ) + 1.0/rsh
        ) + vd*(
            -(
                2.0*isat1*rs*rsh*np.exp(vd/vt)/vt + 0.5*isat2*rs*rsh*np.exp(0.5*vd/vt)/vt
            )/(
                2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
            ) - (
                -2.0*isat1*rs**2*rsh*np.exp(vd/vt)/vt - 0.5*isat2*rs**2*rsh*np.exp(0.5*vd/vt)/vt
            )*(
                2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt
            )/(
                2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
            )**2
        )
    )
    dfrsh_vc = (
        vd*(-(
            2.0*isat1*rsh*(rs*didv + 1)*np.exp(vd/vt)/vt
            + 0.5*isat2*rsh*(rs*didv + 1)*np.exp(0.5*vd/vt)/vt
        )/(
            2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
        ) - (
            -2.0*isat1*rs*rsh*(rs*didv + 1)*np.exp(vd/vt)/vt
            - 0.5*isat2*rs*rsh*(rs*didv + 1)*np.exp(0.5*vd/vt)/vt
        )*(2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt)/(
            2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
        )**2) + (rs*didv + 1)*(
            -(2.0*isat1*rsh*np.exp(vd/vt) + isat2*rsh*np.exp(0.5*vd/vt) + 2.0*vt)/(
                2.0*isat1*rs*rsh*np.exp(vd/vt) + isat2*rs*rsh*np.exp(0.5*vd/vt) + 2.0*rs*vt + 2.0*rsh*vt
            ) + 1.0/rsh
        )
    )
    jac = np.array([
        dfrsh_isat1, dfrsh_isat2, dfrsh_rs, dfrsh_rsh, dfrsh_ic, dfrsh_vc
    ])
    return frsh, jac
