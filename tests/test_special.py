# MagJAX is licensed under the BSD 3-Clause License, see LICENSE.
# Copyright 2024 Sira Pornsiriprasert <code@psira.me>

import numpy as np
import magpylib._src.fields.special_cel as magpy
from pymagba.special import *
import pytest

def test_cel_error() -> None:
    with pytest.raises(ValueError):
        cel(0, 1, 1, 1)

def test_cel() -> None:
    N = 1000
    for kc, p, c, s in np.random.uniform(-5, 5, (N, 4)):
        if kc == 0:
            with pytest.raises(ValueError):
                cel(kc, p, c, s)
                continue

        magjax_cel = cel(kc, p, c, s)
        magpy_cel = magpy.cel0(kc, p, c, s)
        assert magjax_cel == magpy_cel
