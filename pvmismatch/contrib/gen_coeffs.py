"""
Methods to generate diode coefficients.
"""

from pvlib.pvsystem import sapm
import numpy as np
import pandas as pd
from scipy.optimize import root

# IEC 61853 test matrix
TC_C = [15.0, 25.0, 50.0, 75.0]
IRR_W_M2 = [100.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1100.0]
TEST_MAT = np.meshgrid(TC_C, IRR_W_M2)

def gen_iec_61853_from_sapm(pvmodule):
    """
    Generate an IEC 61853 test from Sandia Array Performance Model (sapm).

    :param pvmodule: PV module to be tested
    :type pvmodule: dict

    Module is a dictionary according to :def:`pvlib.pvsystem.sapm`.
    """
    tc, irr = TEST_MAT
    return sapm(irr / 1000.0, tc, pvmodule)


def gen_two_diode(p_mp, v_mp, v_oc, i_sc, nparallel, nseries,
                  irr=IRR_W_M2, tc=TC_C, *args, **kwargs):
    """
    Generate two-diode model parameters for ``pvcell`` given 
    """
    pass


def gen_sapm(iec_61853):
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
