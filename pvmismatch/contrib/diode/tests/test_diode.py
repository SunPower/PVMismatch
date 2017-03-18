"""more tests"""

from pvmismatch.pvmismatch_lib.pvcell import (
    RS as RS_2, RSH as RSH_2, ISAT1_T0 as ISAT1_2, ISAT2 as ISAT2_2
)
from pvmismatch.contrib import diode
import sympy
import numpy as np

RS_1 = 0.0017692138011355  # [OHMS]
RSH_1 = 22.58334768734093  # [OHMS]
ISAT_1 = 1.964978757168584e-008  # [A]
M_1 = 1.339986040349784
V_D = 0.4  # [V]
V_T = 0.026  # [V]


def test_fid():
    """
    test diode current
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
    # evaluate
    test_data = {'i_sat': ISAT_1, 'v_d': V_D, 'm': M_1, 'v_t': V_T}
    fid_test, jid_test = diode.fid(**test_data)
    fid_expected = np.float(i_d.evalf(subs=test_data))
    jid_expected = np.array([
        d__i_sat.evalf(subs=test_data), d__v_d.evalf(subs=test_data),
        d__m.evalf(subs=test_data), d__v_t.evalf(subs=test_data)
    ], dtype=np.float)
    assert np.isclose(fid_test, fid_expected)
    assert np.allclose(jid_test, jid_expected)
    return fid_test, fid_expected


def test_fish():
    """
    test shunt current
    """
    # make sympy symbols
    i_sh, v_d, r_sh = sympy.symbols(['i_sh', 'v_d', 'r_sh'])
    # shunt current
    i_sh = v_d / r_sh
    d__v_d = sympy.diff(i_sh, v_d)
    d__r_sh = sympy.diff(i_sh, r_sh)
    # evaluate
    test_data = {'v_d': V_D, 'r_sh': RSH_1}
    fish_test, jish_test = diode.fish(**test_data)
    fish_expected = np.float(i_sh.evalf(subs=test_data))
    jish_expected = np.array([
        d__v_d.evalf(subs=test_data), d__r_sh.evalf(subs=test_data)
    ], dtype=np.float)
    assert np.isclose(fish_test, fish_expected)
    assert np.allclose(jish_test, jish_expected)
    return fish_test, fish_expected
