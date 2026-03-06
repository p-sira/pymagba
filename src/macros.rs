/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

/// Implements all Pose-related Python properties and transformation methods as a
/// separate `#[pymethods]` impl block. Expand this macro *outside* any existing
/// `#[pymethods]` block so PyO3 can correctly process the `#[getter]`/`#[setter]`
/// attributes.
///
/// Generated methods (matching Magba's Pose API):
/// - `position` property (get/set, `[f64; 3]`)
/// - `orientation` property (get/set, `[f64; 4]` quaternion `[x, y, z, w]`)
/// - `translate(translation: [f64; 3])`
/// - `rotate(q: [f64; 4])`
/// - `rotate_anchor(q: [f64; 4], anchor: [f64; 3])`
///
/// `$struct` must have a field `inner` that exposes the above methods.
#[macro_export]
macro_rules! impl_pypose {
    ($struct:ty) => {
        #[pyo3::pymethods]
        impl $struct {
            /// Position of the object ``[x, y, z]`` in meters.
            #[getter]
            fn position(&self) -> [f64; 3] {
                self.inner.position().into()
            }

            #[setter]
            fn set_position(&mut self, pos: crate::util::ArrayLike3) {
                self.inner.set_position(pos.0);
            }

            /// Orientation as a unit quaternion ``[x, y, z, w]``.
            #[getter]
            fn orientation<'py>(
                &self,
                py: ::pyo3::Python<'py>,
            ) -> ::pyo3::PyResult<::pyo3::Bound<'py, ::pyo3::PyAny>> {
                crate::util::PyRotation(self.inner.orientation()).into_scipy_rotation(py)
            }

            #[setter]
            fn set_orientation(&mut self, rot: crate::util::PyRotation) {
                self.inner.set_orientation(rot.0);
            }

            /// Translate the object by a displacement vector.
            ///
            /// Args:
            ///     translation (list): Displacement ``[dx, dy, dz]`` in meters.
            fn translate(&mut self, translation: crate::util::ArrayLike3) {
                self.inner.translate(translation.0);
            }

            /// Rotate the object about its own origin using a unit quaternion.
            ///
            /// Args:
            ///     rot (Rotation or list): Rotation to apply. Can be a ``scipy.spatial.transform.Rotation``
            ///         object or a unit quaternion as a list.
            fn rotate(&mut self, rot: crate::util::PyRotation) {
                self.inner.rotate(rot.0);
            }

            /// Rotate the object about an arbitrary anchor point using a unit quaternion.
            ///
            /// Args:
            ///     rot (Rotation or list): Rotation to apply.
            ///     anchor (list): Anchor point ``[x, y, z]`` in meters about which to rotate.
            fn rotate_anchor(
                &mut self,
                rot: crate::util::PyRotation,
                anchor: crate::util::ArrayLike3,
            ) {
                self.inner.rotate_anchor(rot.0, anchor.0);
            }
        }
    };
}

/// Implements `compute_B` as a separate `#[pymethods]` impl block.
/// Requires `inner` to implement `magba::base::Source`.
#[macro_export]
macro_rules! impl_compute_B {
    ($struct:ty) => {
        #[pyo3::pymethods]
        impl $struct {
            /// Compute the magnetic flux density **B** at a batch of observer points.
            ///
            /// Args:
            ///     points (numpy.ndarray): Array of shape ``(N, 3)`` containing the observer
            ///         positions ``[x, y, z]`` in meters.
            ///
            /// Returns:
            ///     numpy.ndarray: Array of shape ``(N, 3)`` with the ``[Bx, By, Bz]`` field
            ///     vectors in Tesla at each observer point.
            #[pyo3(name = "compute_B")]
            #[allow(non_snake_case)]
            fn compute_B<'py>(
                &self,
                py: ::pyo3::Python<'py>,
                points: crate::util::PointsLike,
            ) -> ::pyo3::Bound<'py, ::numpy::PyArray2<f64>> {
                use ::magba::base::Source;
                use ::ndarray::Array2;
                use ::numpy::IntoPyArray;

                let pts = points.0;
                let n_points = pts.len();

                let b_field = self.inner.compute_B_batch(&pts);

                let mut out = Array2::<f64>::zeros((n_points, 3));
                for i in 0..n_points {
                    out[[i, 0]] = b_field[i].x;
                    out[[i, 1]] = b_field[i].y;
                    out[[i, 2]] = b_field[i].z;
                }

                out.into_pyarray(py)
            }
        }
    };
}
