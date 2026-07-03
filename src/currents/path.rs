/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::currents::PathCurrent as MagbaPathCurrent;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
    base::{extract_states, try_into_quat, try_into_slice, ArrayLike3, PointsLike, PyRotation},
    macros::{impl_compute_B, impl_pypose},
    util::catch_unwind_to_pyerr,
};
use nalgebra::Vector3;
use numpy::PyArrayMethods;

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct PathCurrent {
    pub(crate) inner: MagbaPathCurrent<f64>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl PathCurrent {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, current=1.0, vertices=None))]
    fn new(
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        current: f64,
        vertices: Option<PointsLike>,
    ) -> PyResult<Self> {
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        let v = vertices
            .map(|v| v.0.into_iter().map(|p| Vector3::new(p.x, p.y, p.z)).collect())
            .unwrap_or_else(|| vec![]);

        catch_unwind_to_pyerr(move || Self {
            inner: MagbaPathCurrent::new(pos, rot, current, v),
        })
    }

    #[getter]
    fn current(&self) -> f64 {
        self.inner.current()
    }

    #[setter]
    fn set_current(&mut self, current: f64) {
        self.inner.set_current(current);
    }

    #[getter]
    fn vertices<'py>(&self, py: Python<'py>) -> Bound<'py, numpy::PyArray2<f64>> {
        let data: Vec<[f64; 3]> = self
            .inner
            .vertices()
            .iter()
            .map(|v| [v.x, v.y, v.z])
            .collect();
        let flat_data: Vec<f64> = data.into_iter().flatten().collect();
        let array = numpy::PyArray1::from_vec(py, flat_data);
        array.reshape([self.inner.vertices().len(), 3]).unwrap()
    }

    #[setter]
    fn set_vertices(&mut self, vertices: PointsLike) -> PyResult<()> {
        let v: Vec<Vector3<f64>> = vertices.0.into_iter().map(|p| Vector3::new(p.x, p.y, p.z)).collect();
        catch_unwind_to_pyerr(std::panic::AssertUnwindSafe(move || {
            self.inner.set_vertices(v);
        }))
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<pyo3::types::PyDict>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        dict.set_item("current", self.inner.current())?;
        
        let vertices_data: Vec<[f64; 3]> = self
            .inner
            .vertices()
            .iter()
            .map(|v| [v.x, v.y, v.z])
            .collect();
        dict.set_item("vertices", vertices_data)?;
        
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, pyo3::types::PyDict>) -> PyResult<()> {
        extract_states!(state, [position;3, orientation;4, current]);
        
        let vertices: Vec<[f64; 3]> = state
            .get_item("vertices")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("vertices"))?
            .extract()?;
        let vertices = vertices.into_iter().map(Vector3::from).collect();

        self.inner = MagbaPathCurrent::new(
            position,
            nalgebra::UnitQuaternion::from_quaternion(orientation.into()),
            current,
            vertices,
        );
        Ok(())
    }
}

impl_pypose!(PathCurrent);
impl_compute_B!(PathCurrent);
