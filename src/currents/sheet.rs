/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::currents::SheetCurrent as MagbaSheetCurrent;
use nalgebra::Vector3;
use pyo3::prelude::*;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::{
    base::{
        extract_states, try_into_quat, try_into_slice, ArrayLike3, FacesLike,
        PointsLike, PyRotation,
    },
    macros::{impl_compute_B, impl_pypose},
    util::catch_unwind_to_pyerr,
};

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct SheetCurrent {
    pub(crate) inner: MagbaSheetCurrent<f64>,
    _vertices: Vec<[f64; 3]>,
    _faces: Vec<[usize; 3]>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl SheetCurrent {
    #[new]
    #[pyo3(signature = (position=None, orientation=None, current_densities=None, vertices=None, faces=None))]
    fn new(
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        current_densities: Option<PointsLike>,
        vertices: Option<PointsLike>,
        faces: Option<FacesLike>,
    ) -> PyResult<Self> {
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        
        let cd = current_densities
            .map(|pts| {
                pts.0
                    .into_iter()
                    .map(|p| Vector3::new(p.x, p.y, p.z))
                    .collect::<Vec<_>>()
            })
            .unwrap_or_default();

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
            let mut inner = MagbaSheetCurrent::from_vertices_and_faces(verts, f.clone(), cd)
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

    #[classmethod]
    #[pyo3(signature = (path, position=None, orientation=None, current_densities=None))]
    fn from_stl(
        _cls: &Bound<'_, pyo3::types::PyType>,
        path: String,
        position: Option<ArrayLike3>,
        orientation: Option<PyRotation>,
        current_densities: Option<PointsLike>,
    ) -> PyResult<Self> {
        let mut file = std::fs::File::open(&path)
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to open file: {}", e)))?;
        
        let mesh = stl_io::read_stl(&mut file)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Failed to read STL: {}", e)))?;
        
        let vertices = mesh.vertices.iter().map(|v| [v[0] as f64, v[1] as f64, v[2] as f64]).collect::<Vec<_>>();
        let faces = mesh.faces.iter().map(|f| [f.vertices[0], f.vertices[1], f.vertices[2]]).collect::<Vec<_>>();
        
        let verts = vertices.iter().map(|v| Vector3::new(v[0], v[1], v[2])).collect::<Vec<_>>();

        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        
        let cd = current_densities
            .map(|pts| {
                pts.0
                    .into_iter()
                    .map(|p| Vector3::new(p.x, p.y, p.z))
                    .collect::<Vec<_>>()
            })
            .unwrap_or_default();

        catch_unwind_to_pyerr(move || {
            let mut inner = MagbaSheetCurrent::from_vertices_and_faces(verts, faces.clone(), cd)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("{:?}", e)))?;
            inner.set_position(Vector3::from(pos));
            inner.set_orientation(rot);
            Ok(Self {
                inner,
                _vertices: vertices,
                _faces: faces,
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
    fn current_densities(&self) -> Vec<[f64; 3]> {
        self.inner.current_densities().iter().map(|v| [v.x, v.y, v.z]).collect()
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<pyo3::types::PyDict>> {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        dict.set_item("current_densities", self.current_densities())?;
        dict.set_item("vertices", self.vertices())?;
        dict.set_item("faces", self.faces())?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, pyo3::types::PyDict>) -> PyResult<()> {
        extract_states!(state, [position;3, orientation;4]);
        
        let cd_obj = state.get_item("current_densities")?.unwrap();
        let current_densities: PointsLike = cd_obj.extract()?;
        let cd = current_densities.0.into_iter().map(|p| Vector3::new(p.x, p.y, p.z)).collect::<Vec<_>>();

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
        let mut inner = MagbaSheetCurrent::from_vertices_and_faces(v.clone(), f.0, cd)
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

impl_pypose!(SheetCurrent);
impl_compute_B!(SheetCurrent);
