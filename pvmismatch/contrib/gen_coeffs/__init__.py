"""
Methods to generate diode coefficients.
"""

from pvlib.pvsystem import sapm
import numpy as np
from scipy import optimize
from pvmismatch.contrib.gen_coeffs import diode, two_diode
from pvmismatch.pvmismatch_lib.pvcell import ISAT1_T0, ISAT2_T0, RS, RSH

# IEC 61853 test matrix
TC_C = [15.0, 25.0, 50.0, 75.0]
IRR_W_M2 = [100.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1100.0]
TEST_MAT = np.meshgrid(TC_C, IRR_W_M2)  #: IEC61853 test matrix

def gen_iec_61853_from_sapm(pvmodule):
    """
    Generate an IEC 61853 test from Sandia Array Performance Model (sapm).

    :param dict pvmodule: PV module to be tested
    :returns: a pandas dataframe with columns ``i_mp``, ``v_mp``, ``i_sc``, and
        ``v_oc`` and rows corresponding to the IEC61853 test conditions

    Module is a dictionary according to ``pvlib.pvsystem.sapm``.
    """
    tc, irr = TEST_MAT
    # sapm in pvlib.pvsystem expects effective_irradiance in W/m2, temp_cell in degrees Celsius
    return sapm(irr, tc, pvmodule)


def gen_two_diode(isc, voc, imp, vmp, nseries, nparallel,
                  tc, x0=None, *args, **kwargs):
    """
    Generate two-diode model parameters for ``pvcell`` given.

    :param numeric isc: short circuit current [A]
    :param numeric voc: open circuit voltage [V]
    :param numeric imp: max power current [A]
    :param numeric vmp: max power voltage [V]
    :param int nseries: number of cells in series
    :param int nparallel: number of parallel substrings in PV module
    :param numeric tc: cell temperature [C]
    :param x0: optional list of initial guesses, default is ``None``
    :returns: tuple ``(isat1, isat2, rs, rsh)`` of generated coefficients and
        the solver output
    """
    isc_cell = isc / nparallel
    voc_cell = voc / nseries
    imp_cell = imp / nparallel
    vmp_cell = vmp / nseries
    if x0 is None:
        isat1 = ISAT1_T0  # [A]
        isat2 = ISAT2_T0
        rs = RS  # [ohms]
        rsh = RSH  # [ohms]
    else:
        isat1 = x0[0]
        isat2 = x0[1]
        rs = x0[2]
        rsh = x0[3]
    x = np.array([np.log(isat1), np.log(isat2), np.sqrt(rs), np.sqrt(rsh)])
    sol = optimize.root(
        fun=residual_two_diode, x0=x,
        args=(isc_cell, voc_cell, imp_cell, vmp_cell, tc),
        jac=True,
        *args, **kwargs
    )
    if sol.success:
        isat1 = np.exp(sol.x[0])
        isat2 = np.exp(sol.x[1])
        rs = sol.x[2] ** 2.0
        rsh = sol.x[3] ** 2.0
    return (isat1, isat2, rs, rsh), sol


def gen_sapm(iec_61853):
    i_sc = iec_61853['i_sc']
    # calculate Isc0 and alpha_Isc
    # given Isc = Ee * Isc0 * (1 + alpha_Isc * (Tc - T0))
    # as Ee * Isc0 + Ee * Isc0 * alpha_Isc * (Tc - T0) = Isc
    # so Ax = B
    # where x0 = Isc0 and x1 = Isc0 * alpha_Isc
    # and A = [Ee, Ee * (Tc - T0)] and B = Isc
    tc, irr = TEST_MAT
    ee = (irr / 1000.0).flatten()
    delta_t = (tc - 25.0).flatten()
    a = np.array([ee, ee * delta_t])
    b = i_sc.flatten()
    x, res, rank, s = np.linalg.lstsq(a.T, b.T)
    isc0, alpha_isc = x[0], x[1] / x[0]
    return isc0, alpha_isc


def residual_two_diode(x, isc, voc, imp, vmp, tc):
    """
    Objective function to solve 2-diode model.

    :param x: parameters ``isat1``, ``isat2``, ``rs``, and ``rsh``
    :param isc: short circuit current [A] at ``tc`` [C]
    :param voc: open circuit voltage [V] at ``tc`` [C]
    :param imp: max power current [A] at ``tc`` [C]
    :param vmp: max power voltage [V] at ``tc`` [C]
    :param tc: cell temperature [C]
    :returns: norm of the residuals and the Jacobian matrix
    """
    # Constants
    q = diode.QE  # [C/electron] elementary electric charge
    # (n.b. 1 Coulomb = 1 A * s)
    kb = diode.KB  # [J/K/molecule] Boltzmann's constant
    tck = tc + 273.15  # [K] reference temperature
    # Governing Equation
    vt = kb * tck / q  # [V] thermal voltage
    # Rescale Variables
    isat1_t0 = np.exp(x[0])
    isat2_t0 = np.exp(x[1])
    rs = x[2] ** 2.0
    rsh = x[3] ** 2.0
    # first diode saturation current
    isat1 = diode.isat_t(tc, isat1_t0)
    isat2 = diode.isat_t(tc, isat2_t0)
    # Short Circuit
    vd_isc, _ = diode.fvd(vc=0.0, ic=isc, rs=rs)
    id1_isc, _ = diode.fid(isat=isat1, vd=vd_isc, m=1.0, vt=vt)
    id2_isc, _ = diode.fid(isat=isat2, vd=vd_isc, m=2.0, vt=vt)
    ish_isc, _ = diode.fish(vd=vd_isc, rsh=rsh)
    # Photo-generated Current
    iph = isc + id1_isc + id2_isc + ish_isc  # [A]
    # Open Circuit
    vd_voc, jvd_voc = diode.fvd(vc=voc, ic=0.0, rs=rs)
    id1_voc, jid1_voc = diode.fid(isat=isat1, vd=vd_voc, m=1.0, vt=vt)
    id2_voc, jid2_voc = diode.fid(isat=isat2, vd=vd_voc, m=2.0, vt=vt)
    ish_voc, jish_voc = diode.fish(vd=vd_voc, rsh=rsh)
    # Max Power Point
    vd_mpp, jvd_mpp = diode.fvd(vc=vmp, ic=imp, rs=rs)
    id1_mpp, jid1_mpp = diode.fid(isat=isat1, vd=vd_mpp, m=1.0, vt=vt)
    id2_mpp, jid2_mpp = diode.fid(isat=isat2, vd=vd_mpp, m=2.0, vt=vt)
    ish_mpp, jish_mpp = diode.fish(vd=vd_mpp, rsh=rsh)
    # Slope at Max Power Point
    dpdv, jdpdv = two_diode.fdpdv(
        isat1=isat1, isat2=isat2, rs=rs, rsh=rsh, ic=imp, vc=vmp, vt=vt
    )
    # Shunt Resistance
    frsh, jrsh = two_diode.fjrsh(
        isat1=isat1, isat2=isat2, rs=rs, rsh=rsh, vt=vt, isc=isc
    )
    # Residual
    # should be (M, ) array with M residual equations (constraints)
    f2 = np.stack([
        (iph - id1_voc - id2_voc - ish_voc).T,  # Open Circuit
        (iph - id1_mpp - id2_mpp - ish_mpp - imp).T,  # Max Power Point
        dpdv.T,  # Slope at Max Power Point
        frsh.T  # Shunt Resistance
    ], axis=0).flatten()
    # Jacobian
    # should be (M, N) array with M residuals and N variables
    # [[df1/dx1, df1/dx2, ...], [df2/dx1, df2/dx2, ...]]
    jvoc = np.stack((
        -jid1_voc[0],  # d/disat1
        -jid2_voc[0],  # d/disat2
        -jvd_voc[2] * (jid1_voc[1] + jid2_voc[1] + jish_voc[0]),  # d/drs
        -jish_voc[1]  # d/drsh
    ), axis=0).T.reshape(-1, 4)
    jmpp = np.stack((
        -jid1_mpp[0],  # d/disat1
        -jid2_mpp[0],  # d/disat2
        -jvd_mpp[2] * (jid1_mpp[1] + jid2_mpp[1] + jish_mpp[0]),  # d/drs
        -jish_mpp[1]  # d.drsh
    ), axis=0).T.reshape(-1, 4) 
    # Scaling Factors
    scale_fx = np.array([np.exp(x[0]), np.exp(x[1]), 2 * x[2], 2 * x[3]])
    # scales each column by the corresponding element
    j2 = np.concatenate(
        (jvoc, jmpp, jdpdv[:4].T.reshape(-1, 4), jrsh[:4].T.reshape(-1, 4)),
        axis=0
    ) * scale_fx
    return f2, j2


PVMODULES = {
    "SunPower_SPR_E20_435": {
        "Vintage": "2013-01-01",
        "Area": 2.16,
        "Material": "c-Si",
        "Cells_in_Series": 128,
        "Parallel_Strings": 1,
        "Isco": 6.4293,
        "Voco": 86.626,
        "Impo": 6.0102,
        "Vmpo": 72.3771,
        "Aisc": 0.00037,
        "Aimp": 7.02e-05,
        "C0": 1.0115,
        "C1": -0.0115,
        "C2": 0.218474,
        "C3": -7.224183,
        "Bvoco": -0.248,
        "Mbvoc": 0.0,
        "Bvmpo": -0.2584,
        "Mbvmp": 0.0,
        "N": 1.011,
        "A0": 0.957,
        "A1": 0.0402,
        "A2": -0.008515,
        "A3": 0.0007141,
        "A4": -2.132e-05,
        "B0": 1.0002,
        "B1": -0.000213,
        "B2": 3.63416e-05,
        "B3": -2.175e-06,
        "B4": 5.2796e-08,
        "B5": -4.4351e-10,
        "DTC": 3.0,
        "FD": 1.0,
        "A": -3.46,
        "B": -0.07599,
        "IXO": 6.1717,
        "IXXO": 4.3997,
        "C4": 0.9891,
        "C5": 0.0109,
        "C6": 1.0869,
        "C7": -0.0869,
        "Notes": "Source: Estimated"
    }
}
