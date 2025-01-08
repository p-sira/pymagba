# Magba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

import pymagba_binding as pmb

def cel(kc: float, p: float, b: float, s: float) -> float:
    return pmb.special.cel(kc, p, b, s)
