/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::sensors::hall_effect::LinearHallSensor as MagbaLinearHallSensor;
use pyo3::prelude::*;

use crate::impl_pypose;

#[pyclass(subclass, from_py_object)]
#[derive(Clone)]
pub struct LinearHallSensor {
    pub(crate) inner: MagbaLinearHallSensor<f64>,
}

#[pymethods]
impl LinearHallSensor {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, sensitive_axis=None, sensitivity=1.0, supply_voltage=5.0))]
    fn new(
        position: Option<crate::util::ArrayLike3>,
        orientation: Option<crate::util::PyRotation>,
        sensitive_axis: Option<crate::util::ArrayLike3>,
        sensitivity: f64,
        supply_voltage: f64,
    ) -> Self {
        let pos = position.map(|p| p.0).unwrap_or([0.0, 0.0, 0.0]);
        let rot = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);
        let s_axis = sensitive_axis.map(|a| a.0).unwrap_or([0.0, 0.0, 1.0]);

        Self {
            inner: MagbaLinearHallSensor::new(pos, rot, s_axis, sensitivity, supply_voltage),
        }
    }

    #[getter]
    fn sensitive_axis(&self) -> [f64; 3] {
        let a = self.inner.sensitive_axis();
        [a.x, a.y, a.z]
    }

    #[setter]
    fn set_sensitive_axis(&mut self, axis: crate::util::ArrayLike3) {
        let sensitivity = self.inner.sensitivity();
        let new_inner = MagbaLinearHallSensor::new(
            self.inner.position(),
            self.inner.orientation(),
            axis.0,
            sensitivity,
            self.inner.supply_voltage(),
        );
        self.inner = new_inner;
    }

    #[getter]
    fn sensitivity(&self) -> f64 {
        self.inner.sensitivity()
    }

    #[setter]
    fn set_sensitivity(&mut self, sensitivity: f64) {
        self.inner.set_sensitivity(sensitivity);
    }

    #[getter]
    fn supply_voltage(&self) -> f64 {
        self.inner.supply_voltage()
    }

    #[setter]
    fn set_supply_voltage(&mut self, voltage: f64) {
        self.inner.set_supply_voltage(voltage);
    }
}

impl_pypose!(LinearHallSensor);
impl_read_voltage!(LinearHallSensor);
