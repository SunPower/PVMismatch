"""
Two diode model tests.
"""

import sympy


def test_didv():
    """
    Test derivative of current vs. voltage.
    """
    
    # NOTES: dI/dV = d(Iph - Id - Ish)/dV
    # d(Iph)/dV = 0
    # d(Id1)/dV = i_sat1*exp(v_d/VT)*(1/VT+dI/dV*r_s/VT)
    # d(Id2)/dV = i_sat2*exp(v_d/2/VT)*(1/2/VT+dI/dV*r_s/2/VT)
    # d(Ish)/dV = 1/r_sh+dI/dV*r_s/r_sh
    # combining dI/dV terms from LHS and RHS yields:
    # dI/dV = 0 - dId1/dV - dId2/dV - dIsh/dV
    # = - i_sat1*exp(v_d/VT)*(1/VT+dI/dV*r_s/VT) ...
    #   - i_sat2*exp(v_d/2/VT)*(1/2/VT+dI/dV*r_s/2/VT) ...
    #   - (1/r_sh+dI/dV*r_s/r_sh)
    # (1+i_sat1*exp(v_d/VT)*r_s/VT+i_sat2*exp(v_d/2/VT)*r_s/2/VT+r_s/r_sh)*dI/dV ...
    #   = -i_sat1*exp(v_d/VT)*1/VT-i_sat2*exp(v_d/2/VT)*1/2/VT-1/r_sh
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
    d__i_d1__v = sympy.diff(i_d1, v_c)
    d__i_d2__v = sympy.diff(i_d2, v_c)
    d__i_sh__v = sympy.diff(i_sh, v_c)
    # dIdV = -(i_sat1/v_t*exp(v_d/v_t)+i_sat2/2/v_t*exp(v_d/2/v_t)+1/r_sh)/ ...
    #     (1+i_sat1*r_s/v_t*exp(v_d/v_t)+i_sat2*r_s/2/v_t*exp(v_d/2/v_t)+r_s/r_sh);
    # JdIdV = jacobian(dIdV,[i_sat1,i_sat2,r_s,r_sh,i_c,v_c]);
    # f = matlabFunction(dIdV,JdIdV,'file','FdIdV','vars',[i_sat1,i_sat2,r_s,r_sh,v_t,i_c,v_c]);
