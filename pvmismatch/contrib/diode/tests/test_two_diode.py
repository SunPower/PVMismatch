"""
Two diode model tests.
"""

import sympy
import numpy as np
from pvmismatch.contrib.diode.two_diode import fdidv
from pvmismatch.contrib.diode.tests.test_diode import (
    ISAT1_2, ISAT2_2, RS_2, RSH_2, V_T, ISC0, I_C, V_C
)
from pvmismatch.contrib.diode.tests import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

V_D = V_C + I_C * RS_2

def test_didv():
    """
    Test derivative of current vs. voltage.
    """
    
    i_sat1, i_sat2, r_s, r_sh, v_t, v_c = sympy.symbols([
        'i_sat1', 'i_sat2', 'r_s', 'r_sh', 'v_t', 'v_c'
    ])
    i_c = sympy.Function('i_c')('v_c')
    i_sc0, alpha_i_sc, t_c, t_0, e_e = sympy.symbols([
        'i_sc', 'alpha_i_sc', 't_c', 't_0', 'e_e'
    ])
    # short circuit
    i_sc = i_sc0 * (1 + alpha_i_sc * (t_c - t_0))
    v_d_sc = i_sc * r_s
    i_d1_sc = i_sat1 * (sympy.exp(v_d_sc / v_t) - 1.0)
    i_d2_sc = i_sat2 * (sympy.exp(v_d_sc / 2.0 / v_t) - 1.0)
    i_sh_sc = v_d_sc / r_sh
    a_ph = 1.0 + (i_d1_sc + i_d2_sc + i_sh_sc) / i_sc
    # any current
    i_ph = a_ph * e_e * i_sc
    v_d = v_c + i_c * r_s
    i_d1 = i_sat1 * (sympy.exp(v_d / v_t) - 1.0)
    i_d2 = i_sat2 * (sympy.exp(v_d / 2.0 / v_t) - 1.0)
    i_sh = v_d / r_sh
    # derivatives of i_c = i_ph - i_d1 - i_d2 - i_sh
    d__i_ph__v = sympy.diff(i_ph, v_c)
    # d(Iph)/dV = 0
    d__i_d1__v = sympy.diff(i_d1, v_c)
    # d(Id1)/dV = i_sat1*exp(v_d/v_t)*(1/v_t+dI/dV*r_s/v_t)
    d__i_d2__v = sympy.diff(i_d2, v_c)
    # d(Id2)/dV = i_sat2*exp(v_d/2/v_t)*(1/2/v_t+dI/dV*r_s/2/v_t)
    d__i_sh__v = sympy.diff(i_sh, v_c)
    # d(Ish)/dV = 1/r_sh+dI/dV*r_s/r_sh
    di_dv = sympy.Derivative(i_c, v_c)
    # 0 = dI/dV - d(Iph - Id1 - Id2 - Ish)/dV
    # 0 = dI/dV - 0 + dId1/dV + dId2/dV + dIsh/dV
    f = di_dv - d__i_ph__v + d__i_d1__v + d__i_d2__v + d__i_sh__v
    # expand the derivative expressions:
    # dI/dV = - i_sat1 * exp(v_d / v_t) * (1 / v_t + dI/dV * r_s / v_t)
    #         - i_sat2 * exp(v_d / 2 / v_t) * (1 / 2 / v_t + dI/dV * r_s / 2 / v_t)
    #         - (1 / r_sh + dI/dV * r_s / r_sh)
    # combine dI/dV terms from LHS and RHS:
    # dI/dV * (1 + i_sat1 * exp(v_d / v_t) * r_s / v_t
    #          + i_sat2 * exp(v_d / 2 / v_t) * r_s / 2 / v_t
    #          + r_s /r_sh)
    #   = - i_sat1 * exp(v_d / v_t) * 1 / v_t
    #     - i_sat2 * exp(v_d / 2 / v_t) * 1 / 2 / v_t
    #     - 1 / r_sh
    g = sympy.solve(f, di_dv)
    if len(g) != 1:
        raise Exception('No solution!')
    di_dv_sol = g[0].subs('v_c + i_c(v_c) * r_s', 'v_d')
    # test fdidv
    test_data = {'i_sat1': ISAT1_2, 'i_sat2': ISAT2_2, 'r_s': RS_2,
                 'r_sh': RSH_2, 'i_c': I_C, 'v_c': V_C, 'v_t': V_T}
    fdidv_test, jdidv_test = fdidv(**test_data)
    expected_data = {'i_sat1': ISAT1_2, 'i_sat2': ISAT2_2, 'r_s': RS_2,
                 'r_sh': RSH_2, 'v_d': V_D, 'v_t': V_T}
    fdidv_expected = np.float(di_dv_sol.evalf(subs=expected_data))
    LOGGER.debug('fdvdi test: %g, expected: %g', fdidv_test, fdidv_expected)
    # dIdV = -(i_sat1 / v_t * exp(v_d / v_t)
    #          + i_sat2 / 2 / v_t * exp(v_d / 2 / v_t)
    #          + 1 / r_sh)
    #   / (1 + i_sat1 * r_s / v_t * exp(v_d / v_t)
    #      + i_sat2 * r_s / 2 / v_t * exp(v_d / 2 / v_t)
    #      + r_s / r_sh)
    # simplify and multiply by 2 * v_t * r_sh:
    # dIdV = -(2 * i_sat1 * r_sh * exp(v_d / v_t)
    #          + i_sat2 * r_sh * exp(v_d / 2 / v_t)
    #          + 2 * v_t)
    #   / (2 * r_sh * v_t
    #      + 2 * i_sat1 * r_s * r_sh * exp(v_d / v_t)
    #      + i_sat2 * r_s * r_sh * exp(v_d / 2 / v_t)
    #      + 2 * r_s * v_t)
    # jacobian
    d__di_dv__i_sat1 = g[0].diff(i_sat1).subs('v_c + i_c(v_c) * r_s', 'v_d')
    jdidv_expected = np.array([
        d__di_dv__i_sat1.evalf(subs=dict(test_data, v_d=V_D))
    ], dtype=np.float)
    LOGGER.debug('jdvdi test: %g, expected: %g', jdidv_test, jdidv_expected)

