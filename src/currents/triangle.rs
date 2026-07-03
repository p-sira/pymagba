/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::currents::TriangleCurrent as MagbaTriangleCurrent;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
    base::{extract_states, try_into_quat, try_into_slice, ArrayLike3, PyRotation},
    macros::{impl_compute_B, impl_pypose},
    util::catch_unwind_to_pyerr,
};
use nalgebra::Vector3;

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct TriangleCurrent {
    pub(crate) inner: MagbaTriangleCurrent<f64>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl TriangleCurrent {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, current_density=None, vertices=None))]
    fn new(
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        current_density: Option<ArrayLike3>,
        vertices: Option<[[f64; 3]; 3]>,
    ) -> PyResult<Self> {
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        let cd = try_into_slice!(current_density);
        let verts = vertices.unwrap_or([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]);

        catch_unwind_to_pyerr(move || Self {
            inner: MagbaTriangleCurrent::new(
                pos,
                rot,
                Vector3::new(cd[0], cd[1], cd[2]),
                [
                    Vector3::new(verts[0][0], verts[0][1], verts[0][2]),
                    Vector3::new(verts[1][0], verts[1][1], verts[1][2]),
                    Vector3::new(verts[2][0], verts[2][1], verts[2][2]),
                ],
            ),
        })
    }

    #[getter]
    fn current_density(&self) -> [f64; 3] {
        self.inner.current_density().into()
    }

    #[setter]
    fn set_current_density(&mut self, current_density: ArrayLike3) -> PyResult<()> {
        let opt_cd = Some(current_density);
        let cd = try_into_slice!(opt_cd);
        catch_unwind_to_pyerr(std::panic::AssertUnwindSafe(move || {
            self.inner.set_current_density(Vector3::new(cd[0], cd[1], cd[2]));
        }))
    }

    #[getter]
    fn vertices(&self) -> [[f64; 3]; 3] {
        let v = self.inner.vertices();
        [
            v[0].into(),
            v[1].into(),
            v[2].into(),
        ]
    }

    #[setter]
    fn set_vertices(&mut self, verts: [[f64; 3]; 3]) -> PyResult<()> {
        let v = [
            Vector3::new(verts[0][0], verts[0][1], verts[0][2]),
            Vector3::new(verts[1][0], verts[1][1], verts[1][2]),
            Vector3::new(verts[2][0], verts[2][1], verts[2][2]),
        ];
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
        dict.set_item("current_density", self.current_density())?;
        dict.set_item("vertices", self.vertices())?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, pyo3::types::PyDict>) -> PyResult<()> {
        extract_states!(state, [position;3, orientation;4, current_density;3]);
        
        let vertices: [[f64; 3]; 3] = state
            .get_item("vertices")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("vertices"))?
            .extract()?;

        self.inner = MagbaTriangleCurrent::new(
            position,
            nalgebra::UnitQuaternion::from_quaternion(orientation.into()),
            Vector3::new(current_density[0], current_density[1], current_density[2]),
            [
                Vector3::new(vertices[0][0], vertices[0][1], vertices[0][2]),
                Vector3::new(vertices[1][0], vertices[1][1], vertices[1][2]),
                Vector3::new(vertices[2][0], vertices[2][1], vertices[2][2]),
            ],
        );
        Ok(())
    }
}

impl_pypose!(TriangleCurrent);
impl_compute_B!(TriangleCurrent);
