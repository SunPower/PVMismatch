"""
Test two diode model equations.
"""

import sympy
import numpy as np
from pvmismatch.contrib.diode.two_diode import fdidv, fdpdv
from pvmismatch.contrib.diode.tests.test_diode import (
    ISAT1_2, ISAT2_2, RS_2, RSH_2, VT, ISC0, IC, VC
)
from pvmismatch.contrib.diode.tests import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

VD_2 = VC + IC * RS_2
LOGGER.debug('V_diode_2 = %g', VD_2)

def test_didv():
    """
    Test derivative of IV curve.
    """
    isat1, isat2, rs, rsh, vt, vc = sympy.symbols([
        'isat1', 'isat2', 'rs', 'rsh', 'vt', 'vc'
    ])
    ic = sympy.Function('ic')('vc')
    isc0, alpha_isc, tc, t0, ee = sympy.symbols([
        'isc', 'alpha_isc', 'tc', 't0', 'ee'
    ])
    # short circuit
    isc = isc0 * (1 + alpha_isc * (tc - t0))
    v_d_sc = isc * rs
    i_d1_sc = isat1 * (sympy.exp(v_d_sc / vt) - 1.0)
    i_d2_sc = isat2 * (sympy.exp(v_d_sc / 2.0 / vt) - 1.0)
    i_sh_sc = v_d_sc / rsh
    aph = 1.0 + (i_d1_sc + i_d2_sc + i_sh_sc) / isc
    # any current
    iph = aph * ee * isc
    vd = vc + ic * rs
    id1 = isat1 * (sympy.exp(vd / vt) - 1.0)
    id2 = isat2 * (sympy.exp(vd / 2.0 / vt) - 1.0)
    ish = vd / rsh
    # derivatives
    diph_dv = sympy.diff(iph, vc)
    did1_dv = sympy.diff(id1, vc)
    did2_dv = sympy.diff(id2, vc)
    dish_dv = sympy.diff(ish, vc)
    di_dv = sympy.Derivative(ic, vc)
    # 0 = ic - (iph - id1 - id2 - ish)
    # 0 = dI/dV - d(Iph - Id1 - Id2 - Ish)/dV
    f = di_dv - diph_dv + did1_dv + did2_dv + dish_dv
    solution_set = sympy.solve(f, di_dv)
    didv = solution_set[0]
    # test fdidv
    test_data = {'isat1': ISAT1_2, 'isat2': ISAT2_2, 'rs': RS_2,
                 'rsh': RSH_2, 'ic': IC, 'vc': VC, 'vt': VT}
    fdidv_test, jdidv_test = fdidv(**test_data)
    expected_data = {
        'isat1': ISAT1_2, 'isat2': ISAT2_2, 'rs': RS_2, 'rsh': RSH_2,
        'ic(vc)': IC, 'vc': VC, 'vd': VD_2, 'vt': VT
    }
    didv_simple = didv.subs('vc + ic(vc) * rs', 'vd')
    fdidv_expected = np.float(didv_simple.evalf(subs=expected_data))
    LOGGER.debug('fdidv test: %g, expected: %g', fdidv_test, fdidv_expected)
    assert np.isclose(fdidv_test, fdidv_expected)
    # jacobian
    d_didv_isat1 = didv.diff(isat1).subs('vc + ic(vc) * rs', 'vd')
    d_didv_isat2 = didv.diff(isat2).subs('vc + ic(vc) * rs', 'vd')
    d_didv_rs = didv.diff(rs).subs('vc + ic(vc) * rs', 'vd')
    d_didv_rsh = didv.diff(rsh).subs('vc + ic(vc) * rs', 'vd')
    d_didv_ic = didv.diff(ic).subs('vc + ic(vc) * rs', 'vd')
    d_didv_vc = didv.diff(vc).subs('vc + ic(vc) * rs', 'vd')
    # update expected test data with calculated derivative
    expected_data['Derivative(ic(vc), vc)'] = fdidv_expected
    jdidv_expected = np.array([
        d_didv_isat1.evalf(subs=expected_data),
        d_didv_isat2.evalf(subs=expected_data),
        d_didv_rs.evalf(subs=expected_data),
        d_didv_rsh.evalf(subs=expected_data),
        d_didv_ic.evalf(subs=expected_data),
        d_didv_vc.evalf(subs=expected_data)
    ], dtype=np.float)
    LOGGER.debug('jdidv test: %r, expected: %r', jdidv_test, jdidv_expected)
    assert np.allclose(jdidv_test, jdidv_expected)
    # power
    dpdv = didv * vc + ic
    # test fdpdv
    fdpdv_test, jdpdv_test = fdpdv(**test_data)
    dpdv_simple = dpdv.subs('vc + ic(vc) * rs', 'vd')
    fdpdv_expected = np.float(dpdv_simple.evalf(subs=expected_data))
    LOGGER.debug('fdpdv test: %g, expected: %g', fdpdv_test, fdpdv_expected)
    assert np.isclose(fdpdv_test, fdpdv_expected)
    # jacobian
    d_dpdv_isat1 = dpdv.diff(isat1).subs('vc + ic(vc) * rs', 'vd')
    d_dpdv_isat2 = dpdv.diff(isat2).subs('vc + ic(vc) * rs', 'vd')
    d_dpdv_rs = dpdv.diff(rs).subs('vc + ic(vc) * rs', 'vd')
    d_dpdv_rsh = dpdv.diff(rsh).subs('vc + ic(vc) * rs', 'vd')
    d_dpdv_ic = dpdv.diff(ic).subs('vc + ic(vc) * rs', 'vd')
    d_dpdv_vc = dpdv.diff(vc).subs('vc + ic(vc) * rs', 'vd')
    jdpdv_expected = np.array([
        d_dpdv_isat1.evalf(subs=expected_data),
        d_dpdv_isat2.evalf(subs=expected_data),
        d_dpdv_rs.evalf(subs=expected_data),
        d_dpdv_rsh.evalf(subs=expected_data),
        d_dpdv_ic.evalf(subs=expected_data),
        d_dpdv_vc.evalf(subs=expected_data)
    ], dtype=np.float)
    LOGGER.debug('jdidv test: %r, expected: %r', jdpdv_test, jdpdv_expected)
    assert np.allclose(jdpdv_test, jdpdv_expected)
    return dpdv_simple
