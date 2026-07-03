/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::magnets::TriangleMagnet as MagbaTriangleMagnet;
use nalgebra::Vector3;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
    base::{
        extract_states, try_into_quat, try_into_slice, try_into_slice_or, ArrayLike3, PyRotation,
    },
    macros::{impl_compute_B, impl_pypose},
    util::catch_unwind_to_pyerr,
};

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct TriangleMagnet {
    pub(crate) inner: MagbaTriangleMagnet<f64>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl TriangleMagnet {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, polarization=None, vertices=None))]
    fn new(
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        polarization: Option<ArrayLike3>,
        vertices: Option<[[f64; 3]; 3]>,
    ) -> PyResult<Self> {
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        let pol = try_into_slice_or!(polarization, [0.0, 0.0, 1.0]);
        let verts = vertices.unwrap_or([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]);

        let v = [
            Vector3::new(verts[0][0], verts[0][1], verts[0][2]),
            Vector3::new(verts[1][0], verts[1][1], verts[1][2]),
            Vector3::new(verts[2][0], verts[2][1], verts[2][2]),
        ];

        catch_unwind_to_pyerr(move || Self {
            inner: MagbaTriangleMagnet::new(pos, rot, pol, v),
        })
    }

    #[getter]
    fn vertices(&self) -> [[f64; 3]; 3] {
        let v = self.inner.vertices();
        [
            [v[0].x, v[0].y, v[0].z],
            [v[1].x, v[1].y, v[1].z],
            [v[2].x, v[2].y, v[2].z],
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

    #[getter]
    fn polarization(&self) -> [f64; 3] {
        self.inner.polarization().into()
    }

    #[setter]
    fn set_polarization(&mut self, pol: ArrayLike3) {
        self.inner.set_polarization(pol.0);
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<pyo3::types::PyDict>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        dict.set_item("polarization", <[f64; 3]>::from(self.inner.polarization()))?;
        dict.set_item("vertices", self.vertices())?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, pyo3::types::PyDict>) -> PyResult<()> {
        extract_states!(state, [position;3, orientation;4, polarization;3]);
        let vertices: [[f64; 3]; 3] = state.get_item("vertices")?.unwrap().extract()?;

        let v = [
            Vector3::new(vertices[0][0], vertices[0][1], vertices[0][2]),
            Vector3::new(vertices[1][0], vertices[1][1], vertices[1][2]),
            Vector3::new(vertices[2][0], vertices[2][1], vertices[2][2]),
        ];

        self.inner = MagbaTriangleMagnet::new(
            position,
            nalgebra::UnitQuaternion::from_quaternion(orientation.into()),
            polarization,
            v,
        );
        Ok(())
    }
}

impl_pypose!(TriangleMagnet);
impl_compute_B!(TriangleMagnet);
