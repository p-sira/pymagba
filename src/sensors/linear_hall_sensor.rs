/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::sensors::hall_effect::LinearHallSensor as MagbaLinearHallSensor;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
    base::{
        extract_states, try_into_quat, try_into_slice, try_into_slice_or, ArrayLike3, PyRotation,
        SourceRef,
    },
    macros::impl_pypose,
    util::catch_unwind_to_pyerr,
};

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct LinearHallSensor {
    pub(crate) inner: MagbaLinearHallSensor<f64>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl LinearHallSensor {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, sensitive_axis=None, sensitivity=1.0, supply_voltage=5.0))]
    fn new(
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        sensitive_axis: Option<ArrayLike3>,
        sensitivity: f64,
        supply_voltage: f64,
    ) -> PyResult<Self> {
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        let s_axis = try_into_slice_or!(sensitive_axis, [0.0, 0.0, 1.0]);

        catch_unwind_to_pyerr(move || Self {
            inner: MagbaLinearHallSensor::new(pos, rot, s_axis, sensitivity, supply_voltage),
        })
    }

    #[getter]
    fn sensitive_axis(&self) -> [f64; 3] {
        let a = self.inner.sensitive_axis();
        [a.x, a.y, a.z]
    }

    #[setter]
    fn set_sensitive_axis(&mut self, axis: ArrayLike3) -> PyResult<()> {
        let sensitivity = self.inner.sensitivity();
        catch_unwind_to_pyerr(std::panic::AssertUnwindSafe(move || {
            let new_inner = MagbaLinearHallSensor::new(
                self.inner.position(),
                self.inner.orientation(),
                axis.0,
                sensitivity,
                self.inner.supply_voltage(),
            );
            self.inner = new_inner;
        }))
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
    fn set_supply_voltage(&mut self, voltage: f64) -> PyResult<()> {
        catch_unwind_to_pyerr(std::panic::AssertUnwindSafe(move || {
            self.inner.set_supply_voltage(voltage);
        }))
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<pyo3::types::PyDict>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        let a = self.inner.sensitive_axis();
        dict.set_item("sensitive_axis", [a.x, a.y, a.z])?;
        dict.set_item("sensitivity", self.inner.sensitivity())?;
        dict.set_item("supply_voltage", self.inner.supply_voltage())?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: pyo3::Bound<'_, pyo3::types::PyDict>) -> PyResult<()> {
        extract_states!(state, [position;3, orientation;4, sensitive_axis;3, sensitivity, supply_voltage]);

        self.inner = MagbaLinearHallSensor::new(
            position,
            nalgebra::UnitQuaternion::from_quaternion(nalgebra::Quaternion::from_vector(
                orientation.into(),
            )),
            sensitive_axis,
            sensitivity,
            supply_voltage,
        );
        Ok(())
    }

    fn __reduce__(&self, py: Python<'_>) -> PyResult<pyo3::Py<pyo3::types::PyTuple>> {
        let cls = py.get_type::<Self>();
        let state = self.__getstate__(py)?;
        let args = pyo3::types::PyTuple::empty(py);
        Ok(pyo3::types::PyTuple::new(
            py,
            [
                cls.into_any(),
                args.into_any(),
                state.into_bound(py).into_any(),
            ],
        )?
        .unbind())
    }

    fn read_voltage(&self, source: pyo3::Bound<'_, pyo3::PyAny>) -> pyo3::PyResult<f64> {
        let source_ref = SourceRef::try_extract(&source)?;
        Ok(self.inner.read_voltage(source_ref.as_source()))
    }

    fn compute_B_perp(&self, source: pyo3::Bound<'_, pyo3::PyAny>) -> pyo3::PyResult<f64> {
        let source_ref = SourceRef::try_extract(&source)?;
        Ok(self.inner.compute_B_perp(source_ref.as_source()))
    }
}

impl_pypose!(LinearHallSensor);
impl_unified_read!(LinearHallSensor, f64, Scalar);
