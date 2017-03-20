"""more tests"""

from pvmismatch.pvmismatch_lib.pvcell import (
    RS as RS_2, RSH as RSH_2, ISAT1_T0 as ISAT1_2, ISAT2 as ISAT2_2
)
from pvmismatch.contrib import diode
from pvmismatch.contrib.gen_coeffs import PVMODULES
from pvmismatch.contrib.diode.tests import logging
import sympy
import numpy as np

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

RS_1 = 0.0017692138011355  # [OHMS]
RSH_1 = 22.58334768734093  # [OHMS]
ISAT_1 = 1.964978757168584e-008  # [A]
M_1 = 1.339986040349784
V_T = 0.026  # [V]
ISC0 = PVMODULES['SunPower_SPR_E20_435']['Isco']  # 6.4293 [A]
I_C = PVMODULES['SunPower_SPR_E20_435']['Impo']  # 6.0102 [A]
V_C = (
    PVMODULES['SunPower_SPR_E20_435']['Vmpo']
    / PVMODULES['SunPower_SPR_E20_435']['Cells_in_Series']
)  # 0.56545 = 72.3771/128 [V]
V_D_1 = V_C + I_C * RS_1  # [V]

LOGGER.debug('I_sc0 = %g', ISC0)
LOGGER.debug('I_mp0 = %g', I_C)
LOGGER.debug('V_mp0 = %g', V_C)
LOGGER.debug('V_diode_1 = %g', V_D_1)


def test_fid():
    """
    Test diode current.
    """
    # make sympy symbols
    i_sat, v_d, m, v_t = sympy.symbols(['i_sat', 'v_d', 'm', 'v_t'])
    # diode current
    i_d = i_sat * (sympy.exp(v_d / m / v_t) - 1.0)
    # derivatives
    d__i_sat = sympy.diff(i_d, i_sat)
    d__v_d = sympy.diff(i_d, v_d)
    d__m = sympy.diff(i_d, m)
    d__v_t = sympy.diff(i_d, v_t)
    # evaluate scalars
    test_data1 = {'i_sat': ISAT_1, 'v_d': V_D_1, 'm': M_1, 'v_t': V_T}
    fid_test, jid_test = diode.fid(**test_data1)
    fid_expected = np.float(i_d.evalf(subs=test_data1))
    jid_expected = np.array([
        d__i_sat.evalf(subs=test_data1), d__v_d.evalf(subs=test_data1),
        d__m.evalf(subs=test_data1), d__v_t.evalf(subs=test_data1)
    ], dtype=np.float)
    LOGGER.debug('test: %g = expected: %g', fid_test, fid_expected)
    assert np.isclose(fid_test, fid_expected)
    assert np.allclose(jid_test, jid_expected.reshape(-1, 1))
    # evaluate arrays
    test_data2 = (np.array([ISAT1_2, ISAT2_2]), np.array([V_D_1, V_D_1]),
                  np.array([1.0, 2.0]), np.array([V_T, V_T]))
    fid_test, jid_test = diode.fid(*test_data2)
    args, math_mod = (i_sat, v_d, m, v_t), ("numpy",)
    f__i_d = sympy.lambdify(args, i_d, modules=math_mod)
    f__d__i_sat = sympy.lambdify(args, d__i_sat, modules=math_mod)
    f__d__v_d = sympy.lambdify(args, d__v_d, modules=math_mod)
    f__d__m = sympy.lambdify(args, d__m, modules=math_mod)
    f__d__v_t = sympy.lambdify(args, d__v_t, modules=math_mod)
    fid_expected = f__i_d(*test_data2)
    jid_expected = np.array([
        f__d__i_sat(*test_data2), f__d__v_d(*test_data2),
        f__d__m(*test_data2), f__d__v_t(*test_data2)
    ], dtype=np.float)
    assert np.allclose(fid_test, fid_expected)
    assert np.allclose(jid_test, jid_expected)


def test_fish():
    """
    test shunt current.
    """
    # make sympy symbols
    i_sh, v_d, r_sh = sympy.symbols(['i_sh', 'v_d', 'r_sh'])
    # shunt current
    i_sh = v_d / r_sh
    d__v_d = sympy.diff(i_sh, v_d)
    d__r_sh = sympy.diff(i_sh, r_sh)
    # evaluate
    test_data = {'v_d': V_D_1, 'r_sh': RSH_1}
    fish_test, jish_test = diode.fish(**test_data)
    fish_expected = np.float(i_sh.evalf(subs=test_data))
    jish_expected = np.array([
        d__v_d.evalf(subs=test_data), d__r_sh.evalf(subs=test_data)
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
    v_d, v_c, i_c, r_s = sympy.symbols(['v_d', 'v_c', 'i_c', 'r_s'])
    # diode voltage
    v_d = v_c + i_c * r_s
    d__v_c = sympy.diff(v_d, v_c)
    d__i_c = sympy.diff(v_d, i_c)
    d__r_s = sympy.diff(v_d, r_s)
    # evaluate
    test_data = {'v_c': V_C, 'i_c': I_C, 'r_s': RS_1}
    fvd_test, jvd_test = diode.fvd(**test_data)
    fvd_expected = np.float(v_d.evalf(subs=test_data))
    jvd_expected = np.array([
        d__v_c.evalf(subs=test_data), d__i_c.evalf(subs=test_data),
        d__r_s.evalf(subs=test_data)
    ], dtype=np.float)
    LOGGER.debug('test: %g = expected: %g', fvd_test, fvd_expected)
    assert np.isclose(fvd_test, fvd_expected)
    assert np.allclose(jvd_test, jvd_expected.reshape(-1, 1))
    # evaluate arrays
