"""
Test common diode model equations.
"""

from pvmismatch.pvmismatch_lib.pvcell import (
    RS as RS_2, RSH as RSH_2, ISAT1_T0 as ISAT1_2, ISAT2_T0 as ISAT2_2
)
from pvmismatch.contrib.gen_coeffs import diode
from pvmismatch.contrib.gen_coeffs import PVMODULES
from pvmismatch.contrib.gen_coeffs.tests import logging
import sympy
import numpy as np

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

RS_1 = 0.0017692138011355  # [OHMS]
RSH_1 = 22.58334768734093  # [OHMS]
ISAT_1 = 1.964978757168584e-008  # [A]
M_1 = 1.339986040349784
VT = 0.026  # [V]
ISC0 = PVMODULES['SunPower_SPR_E20_435']['Isco']  # 6.4293 [A]
IC = PVMODULES['SunPower_SPR_E20_435']['Impo']  # 6.0102 [A]
VC = (
    PVMODULES['SunPower_SPR_E20_435']['Vmpo']
    / PVMODULES['SunPower_SPR_E20_435']['Cells_in_Series']
)  # 0.56545 = 72.3771/128 [V]
VD_1 = VC + IC * RS_1  # [V]

LOGGER.debug('I_sc0 = %g', ISC0)
LOGGER.debug('I_mp0 = %g', IC)
LOGGER.debug('V_mp0 = %g', VC)
LOGGER.debug('V_diode_1 = %g', VD_1)


def test_fid():
    """
    Test diode current.
    """
    # make sympy symbols
    isat, vd, m, vt = sympy.symbols(['isat', 'vd', 'm', 'vt'])
    # diode current
    id_ = isat * (sympy.exp(vd / m / vt) - 1.0)
    # derivatives
    d_isat = sympy.diff(id_, isat)
    d_vd = sympy.diff(id_, vd)
    d_m = sympy.diff(id_, m)
    d_vt = sympy.diff(id_, vt)
    # evaluate scalars
    test_data1 = {'isat': ISAT_1, 'vd': VD_1, 'm': M_1, 'vt': VT}
    fid_test1, jid_test1 = diode.fid(**test_data1)
    fid_expected1 = np.float(id_.evalf(subs=test_data1))
    jid_expected1 = np.array([
        d_isat.evalf(subs=test_data1), d_vd.evalf(subs=test_data1),
        d_m.evalf(subs=test_data1), d_vt.evalf(subs=test_data1)
    ], dtype=np.float)
    LOGGER.debug('test: %g = expected: %g', fid_test1, fid_expected1)
    assert np.isclose(fid_test1, fid_expected1)
    assert np.allclose(jid_test1, jid_expected1.reshape(-1, 1))
    # evaluate arrays
    test_data2 = (np.array([ISAT1_2, ISAT2_2]), np.array([VD_1, VD_1]),
                  np.array([1.0, 2.0]), np.array([VT, VT]))
    fid_test2, jid_test2 = diode.fid(*test_data2)
    # lambda functions
    args, math_mod = (isat, vd, m, vt), ("numpy",)
    g_id = sympy.lambdify(args, id_, modules=math_mod)
    g_d_isat = sympy.lambdify(args, d_isat, modules=math_mod)
    g_d_vd = sympy.lambdify(args, d_vd, modules=math_mod)
    g_d_m = sympy.lambdify(args, d_m, modules=math_mod)
    g_d_vt = sympy.lambdify(args, d_vt, modules=math_mod)
    fid_expected2 = g_id(*test_data2)
    jid_expected2 = np.array([
        g_d_isat(*test_data2), g_d_vd(*test_data2),
        g_d_m(*test_data2), g_d_vt(*test_data2)
    ], dtype=np.float)
    assert np.allclose(fid_test2, fid_expected2)
    assert np.allclose(jid_test2, jid_expected2)


def test_fish():
    """
    test shunt current.
    """
    # make sympy symbols
    ish, vd, rsh = sympy.symbols(['ish', 'vd', 'rsh'])
    # shunt current
    ish = vd / rsh
    d_vd = sympy.diff(ish, vd)
    d_rsh = sympy.diff(ish, rsh)
    # evaluate
    test_data = {'vd': VD_1, 'rsh': RSH_1}
    fish_test, jish_test = diode.fish(**test_data)
    fish_expected = np.float(ish.evalf(subs=test_data))
    jish_expected = np.array([
        d_vd.evalf(subs=test_data), d_rsh.evalf(subs=test_data)
    ], dtype=np.float)
    LOGGER.debug('test: %g = expected: %g', fish_test, fish_expected)
    assert np.isclose(fish_test, fish_expected)
    assert np.allclose(jish_test, jish_expected.reshape(-1, 1))
    # evaluate arrays


def test_fvd():
    """
    Test diode voltage.
    """
    # make sympy symbols
    vd, vc, ic, rs = sympy.symbols(['vd', 'vc', 'ic', 'rs'])
    # diode voltage
    vd = vc + ic * rs
    d_vc = sympy.diff(vd, vc)
    d_ic = sympy.diff(vd, ic)
    d_rs = sympy.diff(vd, rs)
    # evaluate
    test_data = {'vc': VC, 'ic': IC, 'rs': RS_1}
    fvd_test, jvd_test = diode.fvd(**test_data)
    fvd_expected = np.float(vd.evalf(subs=test_data))
    jvd_expected = np.array([
        d_vc.evalf(subs=test_data), d_ic.evalf(subs=test_data),
        d_rs.evalf(subs=test_data)
    ], dtype=np.float)
    LOGGER.debug('test: %g = expected: %g', fvd_test, fvd_expected)
    assert np.isclose(fvd_test, fvd_expected)
    assert np.allclose(jvd_test, jvd_expected.reshape(-1, 1))
    # evaluate arrays
