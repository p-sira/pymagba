import pymagba_binding as pmb
from numpy.typing import NDArray

def axial_cyl_b_cyl(r: float,z: float,radius: float, height: float) -> NDArray:
    return pmb.fields.axial_cyl_b_cyl(r, z, radius, height)