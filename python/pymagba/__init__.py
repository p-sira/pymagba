# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Magba binding for Python.

Providing a high-level Python interface to the Magba magnetic field computation
engine, including various magnetic sources and sensors.
"""

from __future__ import annotations

from .__about__ import *

from . import magnets
from . import sensors
from . import fields
