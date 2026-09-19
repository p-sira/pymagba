# PyMagba is licensed under The 3-Clause BSD, see LICENSE.
# Copyright 2025 Sira Pornsiriprasert <code@psira.me>

"""Magnetic field calculation functions."""

from .pymagba_binding import circular_B, cuboid_B, cylinder_B, dipole_B, sphere_B

__all__ = ["circular_B", "cuboid_B", "cylinder_B", "dipole_B", "sphere_B"]
