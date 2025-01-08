import pymagba_binding as pmb
from numpy.typing import NDArray


def axial_cyl_b_cyl(
    r: float, z: float, radius: float, height: float, pol_z: float
) -> NDArray:
    return pmb.fields.axial_cyl_b_cyl(r, z, radius, height, pol_z)


def axial_cyl_b(
    point: tuple[float, float, float], radius: float, height: float, pol_z: float
) -> NDArray:
    # TODO Still doesn't work with small values
    return pmb.fields.axial_cyl_b(point, radius, height, pol_z)


def diametric_cyl_b_cyl(
    cyl_point: tuple[float, float, float], radius: float, height: float, pol_r: float
) -> NDArray:
    return pmb.fields.diametric_cyl_b_cyl(cyl_point, radius, height, pol_r)


def diametric_cyl_b(
    point: tuple[float, float, float], radius: float, height: float, pol_r: float
) -> NDArray:
    return pmb.fields.diametric_cyl_b(point, radius, height, pol_r)


def cyl_b_cyl(
    cyl_point: tuple[float, float, float], radius: float, height: float, pol_r: float, pol_z: float
) -> NDArray:
    return pmb.fields.cyl_b_cyl(cyl_point, radius, height, pol_r, pol_z)


def cyl_b(
    point: tuple[float, float, float],
    radius: float,
    height: float,
    pol: tuple[float, float, float],
) -> NDArray:
    return pmb.fields.cyl_b(point, radius, height, pol)
