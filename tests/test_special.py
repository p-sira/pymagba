# MagJAX is licensed under the BSD 3-Clause License, see LICENSE.
# Copyright 2024 Sira Pornsiriprasert <code@psira.me>

from math import isnan
import numpy as np
import magpylib._src.fields.special_cel as magpy
from pymagba.special import *

def test_cel_error() -> None:
    assert isnan(cel(0, 1, 1, 1))

def test_cel() -> None:
    N = 1000
    for kc, p, c, s in np.random.uniform(-5, 5, (N, 4)):
        if kc == 0:
            assert isnan(cel(kc, p, c, s))

        magba_cel = cel(kc, p, c, s)
        magpy_cel = magpy.cel0(kc, p, c, s)
        assert magba_cel == magpy_cel
