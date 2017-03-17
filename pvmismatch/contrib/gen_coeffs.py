"""
Methods to generate diode coefficients.
"""

from pvlib.pvsystem import sapm
import numpy as np
import pandas as pd

# IEC 61853 test matrix
TC_C = [15.0, 25.0, 50.0, 75.0]
IRR_W_M2 = [100.0, 200.0, 400.0, 600.0, 800.0, 1000.0, 1100.0]

def gen_iec_61853_from_sapm(pvmodule=PVMODULES['SunPower_SPR_E20_435']):
    """
    Generate an IEC 61853 test from Sandia Array Performance Model (sapm).

    :param pvmodule: PV module to be tested
    :type pvmodule: dict

    Module is a dictionary according to `pvlib.pvsystem.sapm`.
    """
    tc, irr = np.meshgrid(TC_C, IRR_W_M2)
    return sapm(irr / 1000.0, tc, pvmodule)


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
