/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use pyo3::prelude::*;

/// A wrapper for extracting 3-element arrays from Python objects (lists, tuples, numpy arrays).
pub struct ArrayLike3(pub [f64; 3]);

impl<'a, 'py> FromPyObject<'a, 'py> for ArrayLike3 {
    type Error = PyErr;
    fn extract(ob: pyo3::Borrowed<'a, 'py, PyAny>) -> Result<Self, Self::Error> {
        // We use Vec extraction as it handles lists, tuples, and numpy arrays.
        let v: Vec<f64> = ob.extract()?;
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

/// A wrapper for orientation, supporting scipy Rotation and 4-element arrays [x, y, z, w].
pub struct PyRotation(pub nalgebra::UnitQuaternion<f64>);

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
