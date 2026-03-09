/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use pyo3::prelude::*;
use pyo3_stub_gen::{PyStubType, TypeInfo};

/// A wrapper for extracting 3-element arrays from Python objects.
///
/// Supports lists, tuples, and numpy arrays by converting them to a fixed-size
/// array [f64; 3] if they contain exactly 3 elements.
pub struct ArrayLike3(pub [f64; 3]);

impl PyStubType for ArrayLike3 {
    fn type_output() -> TypeInfo {
        TypeInfo {
            name: "typing.Sequence[float]".to_string(),
            import: [pyo3_stub_gen::ImportRef::Module("typing".into())]
                .into_iter()
                .collect(),
            source_module: None,
            type_refs: std::collections::HashMap::new(),
        }
    }
}

impl<'a, 'py> FromPyObject<'a, 'py> for ArrayLike3 {
    type Error = PyErr;
    fn extract(ob: pyo3::Borrowed<'a, 'py, PyAny>) -> Result<Self, Self::Error> {
        // We use numpy to convert to array if it's not already one.
        // This handles lists, tuples, and other sequences naturally.
        let py = ob.py();
        let np = py.import("numpy")?;
        let np_arr = np.call_method1("asarray", (ob,))?;
        let v: Vec<f64> = np_arr.extract()?;

        if v.len() == 3 {
            Ok(ArrayLike3([v[0], v[1], v[2]]))
        } else {
            Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Expected 3 elements, got {}",
                v.len()
            )))
        }
    }
}

/// A wrapper for extracting a batch of 3D points (N, 3).
///
/// Supports lists, tuples, and numpy arrays. Also handles a single 1D point
/// [x, y, z] by converting it to a single-element batch [[x, y, z]].
pub struct PointsLike(pub Vec<nalgebra::Point3<f64>>);

impl PyStubType for PointsLike {
    fn type_output() -> TypeInfo {
        TypeInfo {
            name: "typing.Sequence[typing.Sequence[float]]".to_string(),
            import: [pyo3_stub_gen::ImportRef::Module("typing".into())]
                .into_iter()
                .collect(),
            source_module: None,
            type_refs: std::collections::HashMap::new(),
        }
    }
}

impl<'a, 'py> FromPyObject<'a, 'py> for PointsLike {
    type Error = PyErr;
    fn extract(ob: pyo3::Borrowed<'a, 'py, PyAny>) -> Result<Self, Self::Error> {
        let py = ob.py();
        let np = py.import("numpy")?;
        let np_arr = np.call_method1("asarray", (ob,))?;
        let shape: Vec<usize> = np_arr.getattr("shape")?.extract()?;

        match shape.len() {
            1 if shape[0] == 3 => {
                // Single point [x, y, z]
                let v: Vec<f64> = np_arr.extract()?;
                Ok(PointsLike(vec![nalgebra::Point3::new(v[0], v[1], v[2])]))
            }
            2 if shape[1] == 3 => {
                // Batch of points [[x, y, z], ...]
                let n = shape[0];
                let v: Vec<f64> = np_arr.call_method0("flatten")?.extract()?;
                let mut pts = Vec::with_capacity(n);
                for i in 0..n {
                    pts.push(nalgebra::Point3::new(v[i * 3], v[i * 3 + 1], v[i * 3 + 2]));
                }
                Ok(PointsLike(pts))
            }
            _ => Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Expected shape (3,) or (N, 3), got {:?}",
                shape
            ))),
        }
    }
}

/// A wrapper for orientation transformations.
///
/// Supports scipy.spatial.transform.Rotation objects and 4-element arrays
/// representing quaternions as [x, y, z, w].
pub struct PyRotation(pub nalgebra::UnitQuaternion<f64>);

impl PyStubType for PyRotation {
    fn type_output() -> TypeInfo {
        TypeInfo {
            name: "typing.Union[scipy.spatial.transform.Rotation, typing.Sequence[float]]"
                .to_string(),
            import: [
                pyo3_stub_gen::ImportRef::Module("scipy".into()),
                pyo3_stub_gen::ImportRef::Module("typing".into()),
            ]
            .into_iter()
            .collect(),
            source_module: None,
            type_refs: std::collections::HashMap::new(),
        }
    }
}

impl<'a, 'py> FromPyObject<'a, 'py> for PyRotation {
    type Error = PyErr;
    fn extract(ob: pyo3::Borrowed<'a, 'py, PyAny>) -> Result<Self, Self::Error> {
        // Try calling as_quat() if it's a scipy Rotation
        if let Ok(as_quat) = ob.call_method0("as_quat") {
            let v: Vec<f64> = as_quat.extract()?;
            if v.len() == 4 {
                return Ok(PyRotation(nalgebra::UnitQuaternion::from_quaternion(
                    nalgebra::Quaternion::new(v[3], v[0], v[1], v[2]),
                )));
            }
        }

        // Fallback to 4-element array
        let v: Vec<f64> = ob.extract()?;
        if v.len() == 4 {
            Ok(PyRotation(nalgebra::UnitQuaternion::from_quaternion(
                nalgebra::Quaternion::new(v[3], v[0], v[1], v[2]),
            )))
        } else {
            Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Expected scipy.spatial.transform.Rotation or 4-element array [x, y, z, w], got length {}",
                v.len()
            )))
        }
    }
}

impl PyRotation {
    pub fn into_scipy_rotation<'py>(self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let sc = py.import("scipy.spatial.transform")?;
        let rot_cls = sc.getattr("Rotation")?;
        let q = self.0.into_inner();
        let quat = [q.i, q.j, q.k, q.w];
        rot_cls.call_method1("from_quat", (quat,))
    }
}
