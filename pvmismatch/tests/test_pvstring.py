from pvmismatch import *


def check_same_pvconst_and_lengths(pvstr):
    assert len(pvstr.pvmods) == pvstring.NUMBERMODS
    for p in pvstr.pvmods:
        assert p.pvconst is pvstr.pvconst


def test_pvstring_with_pvmods_list():
    pvmods = [pvmodule.PVmodule()] * pvstring.NUMBERMODS
    pvstr = pvstring.PVstring(pvmods=pvmods)
    check_same_pvconst_and_lengths(pvstr)


def test_pvstring_with_pvmods_obj():
    pvmods = pvmodule.PVmodule()
    pvstr = pvstring.PVstring(pvmods=pvmods)
    check_same_pvconst_and_lengths(pvstr)


def test_pvstring_with_no_pvmods():
    pvstr = pvstring.PVstring()
    check_same_pvconst_and_lengths(pvstr)
