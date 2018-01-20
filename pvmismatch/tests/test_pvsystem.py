from pvmismatch import *


def check_same_pvconst_and_lengths(pvsys):
    assert len(pvsys.pvstrs) == pvsystem.NUMBERSTRS
    for n, p in enumerate(pvsys.pvstrs):
        assert p.pvconst is pvsys.pvconst
        assert len(p.pvmods) == pvsys.numberMods[n]


def test_pvsystem_with_pvstrs_list():
    pvstrs = [pvstring.PVstring()] * pvsystem.NUMBERSTRS
    pvsys = pvsystem.PVsystem(pvstrs=pvstrs)
    check_same_pvconst_and_lengths(pvsys)


def test_pvsystem_with_pvstrs_obj():
    pvstrs = pvstring.PVstring()
    pvsys = pvsystem.PVsystem(pvstrs=pvstrs)
    check_same_pvconst_and_lengths(pvsys)


def test_pvsystem_with_no_pvstrs():
    pvsys = pvsystem.PVsystem()
    check_same_pvconst_and_lengths(pvsys)
