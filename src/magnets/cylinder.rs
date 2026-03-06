/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::magnets::CylinderMagnet as MagbaCylinderMagnet;
use pyo3::prelude::*;

use crate::{impl_compute_B, impl_pypose};

/// Uniformly magnetized cylindrical magnet.
///
/// All dimensions are in SI units (meters, Tesla).
///
/// Args:
///     position (list[float] | None): Center of the cylinder ``[x, y, z]`` in meters.
///         Defaults to ``[0.0, 0.0, 0.0]``.
///     orientation (scipy.spatial.transform.Rotation | list[float] | None): Orientation as a unit quaternion ``[x, y, z, w]`` or a Rotation object.
///         Defaults to the identity quaternion.
///     diameter (float): Cylinder diameter in meters. Must be positive. Defaults to ``1.0``.
///     height (float): Cylinder height in meters. Must be positive. Defaults to ``1.0``.
///     polarization (list[float] | None): Remanence polarization vector ``[Bx, By, Bz]`` in Tesla.
///         Defaults to ``[0.0, 0.0, 0.0]``.
///
/// Examples:
/// ```python
/// from pymagba.magnets import CylinderMagnet
/// from scipy.spatial.transform import Rotation
/// magnet = CylinderMagnet(
///     position=[0.0, 0.0, 0.0],
///     orientation=Rotation.from_euler('x', 90, degrees=True),
///     diameter=0.01,
///     height=0.02,
///     polarization=[0.0, 0.0, 1.0],
/// )
/// ```
///
/// References:
///     Caciagli, Alessio, et al. "Exact Expression for the Magnetic Field of a Finite Cylinder
///     with Arbitrary Uniform Magnetization." Journal of Magnetism and Magnetic Materials 456 (2018): 423-432.
///     https://doi.org/10.1016/j.jmmm.2018.02.003
///
///     Derby, Norman, and Stanislaw Olbert. "Cylindrical Magnets and Ideal Solenoids."
///     American Journal of Physics 78, no. 3 (2010): 229-235.
///     https://doi.org/10.1119/1.3256157
#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct CylinderMagnet {
    pub(crate) inner: MagbaCylinderMagnet<f64>,
}

#[pymethods]
impl CylinderMagnet {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, diameter=1.0, height=1.0, polarization=None))]
    fn new(
        position: Option<crate::util::ArrayLike3>,
        orientation: Option<crate::util::PyRotation>,
        diameter: f64,
        height: f64,
        polarization: Option<crate::util::ArrayLike3>,
    ) -> Self {
        let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let rot = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);
        let pol = polarization.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);

        Self {
            inner: MagbaCylinderMagnet::new(pos, rot, pol, diameter, height),
        }
    }

    /// Cylinder diameter in meters. Must be positive.
    #[getter]
    fn diameter(&self) -> f64 {
        self.inner.diameter()
    }

    #[setter]
    fn set_diameter(&mut self, diameter: f64) {
        self.inner.set_diameter(diameter);
    }

    /// Cylinder height in meters. Must be positive.
    #[getter]
    fn height(&self) -> f64 {
        self.inner.height()
    }

    #[setter]
    fn set_height(&mut self, height: f64) {
        self.inner.set_height(height);
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
}

impl_pypose!(CylinderMagnet);
impl_compute_B!(CylinderMagnet);
