/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
use pyo3::types::PySequence;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::{ImportRef, PyStubType, TypeInfo};

/// A wrapper for extracting 3-element arrays from Python objects.
///
/// Supports lists, tuples, and numpy arrays by converting them to a fixed-size
/// array [f64; 3] if they contain exactly 3 elements.
pub struct ArrayLike3(pub [f64; 3]);

#[cfg(feature = "stub-gen")]
impl PyStubType for ArrayLike3 {
    fn type_output() -> TypeInfo {
        TypeInfo {
            name: "numpy.typing.ArrayLike".to_string(),
            import: [pyo3_stub_gen::ImportRef::Module("numpy.typing".into())]
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
        // 1. Fast path: Extract as a 1D numpy array
        if let Ok(arr1) = ob.extract::<PyReadonlyArray1<'py, f64>>() {
            let view = arr1.as_array();
            let shape = view.shape();

            if shape[0] == 3 {
                return Ok(ArrayLike3([view[0], view[1], view[2]]));
            } else {
                return Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "Expected exactly 3 elements, got shape {:?}",
                    shape
                )));
            }
        }

        // 2. Fallback for native Python lists: [x, y, z]
        if let Ok(list_1d) = ob.extract::<[f64; 3]>() {
            return Ok(ArrayLike3(list_1d));
        }

        // Check if it's a sequence but wrong length
        if let Ok(seq) = ob.cast::<PySequence>() {
            if seq.len().unwrap_or(0) != 3 {
                return Err(pyo3::exceptions::PyValueError::new_err(format!(
                    "Expected exactly 3 elements, got {}",
                    seq.len().unwrap_or(0)
                )));
            }
        }

        Err(pyo3::exceptions::PyTypeError::new_err(
            "Expected a 1D NumPy array of shape (3,) or a sequence of 3 floats.",
        ))
    }
}

/// A wrapper for extracting a batch of 3D points (N, 3).
///
/// Supports lists, tuples, and numpy arrays. Also handles a single 1D point
/// [x, y, z] by converting it to a single-element batch [[x, y, z]].
pub struct PointsLike(pub Vec<nalgebra::Point3<f64>>);

#[cfg(feature = "stub-gen")]
impl PyStubType for PointsLike {
    fn type_output() -> TypeInfo {
        TypeInfo {
            name: "numpy.typing.ArrayLike".to_string(),
            import: [ImportRef::Module("numpy.typing".into())]
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
        // 1. Try extracting as an N x 3 numpy array
        if let Ok(arr2) = ob.extract::<PyReadonlyArray2<'py, f64>>() {
            let view = arr2.as_array();
            let shape = view.shape();

            if shape[1] == 3 {
                let n = shape[0];
                let mut pts = Vec::with_capacity(n);
                for i in 0..n {
                    pts.push(nalgebra::Point3::new(
                        view[[i, 0]],
                        view[[i, 1]],
                        view[[i, 2]],
                    ));
                }
                return Ok(PointsLike(pts));
            }
        }

        // 2. Native Python lists of lists: [[x, y, z], ...]
        if let Ok(list_2d) = ob.extract::<Vec<[f64; 3]>>() {
            let pts = list_2d
                .into_iter()
                .map(|p| nalgebra::Point3::new(p[0], p[1], p[2]))
                .collect();
            return Ok(PointsLike(pts));
        }

        // 3. Delegate to ArrayLike3 for the single point / 1D cases
        // This handles both PyReadonlyArray1 and flat python lists [x, y, z]
        if let Ok(single_point) = ob.extract::<ArrayLike3>() {
            let arr = single_point.0;
            return Ok(PointsLike(vec![nalgebra::Point3::new(
                arr[0], arr[1], arr[2],
            )]));
        }

        Err(pyo3::exceptions::PyTypeError::new_err(
            "Expected a NumPy array of shape (3,) or (N, 3), or a compatible Python list.",
        ))
    }
}

/// A wrapper for orientation transformations.
///
/// Supports scipy.spatial.transform.Rotation objects and 4-element arrays
/// representing quaternions as [x, y, z, w].
pub struct PyRotation(pub nalgebra::UnitQuaternion<f64>);

#[cfg(feature = "stub-gen")]
impl PyStubType for PyRotation {
    fn type_output() -> TypeInfo {
        TypeInfo {
            name: "scipy.spatial.transform.Rotation | numpy.typing.ArrayLike".to_string(),
            import: [
                ImportRef::Module("scipy".into()),
                ImportRef::Module("numpy.typing".into()),
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
        // 1. Try Scipy Rotation (calls `as_quat()` which returns a numpy array)
        if let Ok(as_quat) = ob.call_method0("as_quat") {
            // Extract directly into a fixed-size stack array [f64; 4]
            if let Ok(arr) = as_quat.extract::<[f64; 4]>() {
                return Ok(PyRotation(nalgebra::UnitQuaternion::from_quaternion(
                    nalgebra::Quaternion::new(arr[3], arr[0], arr[1], arr[2]),
                )));
            }
        }

        // 2. Fast path: 1D NumPy array [x, y, z, w] (Zero-copy)
        if let Ok(arr1) = ob.extract::<PyReadonlyArray1<'py, f64>>() {
            let view = arr1.as_array();
            if view.shape()[0] == 4 {
                return Ok(PyRotation(nalgebra::UnitQuaternion::from_quaternion(
                    nalgebra::Quaternion::new(view[3], view[0], view[1], view[2]),
                )));
            }
        }

        // 3. Fast path: Native Python list or tuple (e.g., [x, y, z, w])
        if let Ok(arr) = ob.extract::<[f64; 4]>() {
            return Ok(PyRotation(nalgebra::UnitQuaternion::from_quaternion(
                nalgebra::Quaternion::new(arr[3], arr[0], arr[1], arr[2]),
            )));
        }

        Err(pyo3::exceptions::PyTypeError::new_err(
            "Expected scipy.spatial.transform.Rotation, a (4,) NumPy array, or a 4-element list/tuple [x, y, z, w]."
        ))
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
