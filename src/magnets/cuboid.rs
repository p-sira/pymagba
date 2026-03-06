/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::magnets::CuboidMagnet as MagbaCuboidMagnet;
use pyo3::prelude::*;

use crate::{impl_compute_B, impl_pypose};

/// Uniformly magnetized cuboid magnet.
///
/// All dimensions are in SI units (meters, Tesla).
///
/// Args:
///     position (list, optional): Center of the cuboid ``[x, y, z]`` in meters.
///         Defaults to ``[0.0, 0.0, 0.0]``.
///     orientation (Rotation or list, optional): Orientation as a
///         unit quaternion ``[x, y, z, w]`` or a ``scipy.spatial.transform.Rotation``
///         object. Defaults to the identity quaternion.
///     dimensions (list, optional): Side lengths ``[dx, dy, dz]`` in meters.
///         Defaults to ``[1.0, 1.0, 1.0]``.
///     polarization (list, optional): Remanence polarization vector ``[Bx, By, Bz]`` in Tesla.
///         Defaults to ``[0.0, 0.0, 0.0]``.
///
/// Examples:
///
///     .. code-block:: python
///
///         from pymagba.magnets import CuboidMagnet
///         from scipy.spatial.transform import Rotation
///
///         magnet = CuboidMagnet(
///             position=[0.0, 0.0, 0.0],
///             orientation=Rotation.from_euler('z', 45, degrees=True),
///             dimensions=[0.01, 0.01, 0.02],
///             polarization=[0.0, 0.0, 1.0],
///         )
///
/// References:
///     Ortner, Michael, and Lucas Gabriel Coliado Bandeira. "Magpylib: A Free Python Package
///     for Magnetic Field Computation." SoftwareX 11 (2020): 100466.
///     https://doi.org/10.1016/j.softx.2020.100466
#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct CuboidMagnet {
    pub(crate) inner: MagbaCuboidMagnet<f64>,
}

#[pymethods]
impl CuboidMagnet {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, dimensions=None, polarization=None))]
    fn new(
        position: Option<crate::util::ArrayLike3>,
        orientation: Option<crate::util::PyRotation>,
        dimensions: Option<crate::util::ArrayLike3>,
        polarization: Option<crate::util::ArrayLike3>,
    ) -> Self {
        let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let rot = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);
        let pol = polarization.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let dim = dimensions.map(|d| d.0).unwrap_or([1.0, 1.0, 1.0]);

        Self {
            inner: MagbaCuboidMagnet::new(pos, rot, pol, dim),
        }
    }

    /// Remanence polarization vector ``[Bx, By, Bz]`` in Tesla.
    #[getter]
    fn polarization(&self) -> [f64; 3] {
        self.inner.polarization().into()
    }

    #[setter]
    fn set_polarization(&mut self, pol: crate::util::ArrayLike3) {
        self.inner.set_polarization(pol.0);
    }

    /// Side lengths ``[dx, dy, dz]`` in meters. All values must be non-negative.
    #[getter]
    fn dimensions(&self) -> [f64; 3] {
        self.inner.dimensions().into()
    }

    #[setter]
    fn set_dimensions(&mut self, dim: crate::util::ArrayLike3) {
        self.inner.set_dimensions(dim.0);
    }
}

impl_pypose!(CuboidMagnet);
impl_compute_B!(CuboidMagnet);
