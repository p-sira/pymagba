/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::magnets::MeshMagnet as MagbaMeshMagnet;
use nalgebra::Vector3;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
    base::{
        extract_states, try_into_quat, try_into_slice, try_into_slice_or, ArrayLike3, FacesLike,
        PointsLike, PyRotation,
    },
    macros::{impl_compute_B, impl_pypose},
    util::catch_unwind_to_pyerr,
};

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct MeshMagnet {
    pub(crate) inner: MagbaMeshMagnet<f64>,
    _vertices: Vec<[f64; 3]>,
    _faces: Vec<[usize; 3]>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl MeshMagnet {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, polarization=None, vertices=None, faces=None))]
    fn new(
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        polarization: Option<ArrayLike3>,
        vertices: Option<PointsLike>,
        faces: Option<FacesLike>,
    ) -> PyResult<Self> {
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        let pol = try_into_slice_or!(polarization, [0.0, 0.0, 1.0]);

        let verts = vertices
            .map(|pts| {
                pts.0
                    .into_iter()
                    .map(|p| Vector3::new(p.x, p.y, p.z))
                    .collect::<Vec<_>>()
            })
            .unwrap_or_default();

        let vertices_arr = verts.iter().map(|v| [v.x, v.y, v.z]).collect::<Vec<_>>();

        let f = faces.map(|fs| fs.0).unwrap_or_default();

        catch_unwind_to_pyerr(move || {
            let mut inner = MagbaMeshMagnet::from_vertices_and_faces(verts, f.clone(), pol)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("{:?}", e)))?;
            inner.set_position(Vector3::from(pos));
            inner.set_orientation(rot);
            Ok(Self {
                inner,
                _vertices: vertices_arr,
                _faces: f,
            })
        })?
    }

    #[getter]
    fn vertices(&self) -> Vec<[f64; 3]> {
        self._vertices.clone()
    }

    #[getter]
    fn faces(&self) -> Vec<[usize; 3]> {
        self._faces.clone()
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
        dict.set_item("faces", self.faces())?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, pyo3::types::PyDict>) -> PyResult<()> {
        extract_states!(state, [position;3, orientation;4, polarization;3]);

        let vertices_obj = state.get_item("vertices")?.unwrap();
        let verts: PointsLike = vertices_obj.extract()?;
        let v = verts
            .0
            .into_iter()
            .map(|p| Vector3::new(p.x, p.y, p.z))
            .collect::<Vec<_>>();

        let faces_obj = state.get_item("faces")?.unwrap();
        let f: FacesLike = faces_obj.extract()?;

        let f_clone = f.0.clone();
        let mut inner = MagbaMeshMagnet::from_vertices_and_faces(v.clone(), f.0, polarization)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("{:?}", e)))?;
        inner.set_position(Vector3::from(position));
        inner.set_orientation(nalgebra::UnitQuaternion::from_quaternion(
            orientation.into(),
        ));

        self.inner = inner;
        self._vertices = v.iter().map(|p| [p.x, p.y, p.z]).collect();
        self._faces = f_clone;
        Ok(())
    }
}

impl_pypose!(MeshMagnet);
impl_compute_B!(MeshMagnet);
