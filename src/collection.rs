/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::collections::{SourceAssembly, SourceComponent};
use pyo3::prelude::*;

use crate::{impl_compute_B, impl_pypose, magnets::*};

/// A group of magnetic sources that can be transformed and queried as a unit.
///
/// ``SourceCollection`` wraps a ``SourceAssembly`` from Magba, combining multiple
/// magnetic sources (``CylinderMagnet``, ``CuboidMagnet``, or ``Dipole``) into a single
/// object with its own pose. Transformations applied to the collection move all child
/// sources relative to the collection's reference frame.
///
/// Args:
///     sources (list, optional): Iterable of magnetic sources to include. Each element must be
///         a ``CylinderMagnet``, ``CuboidMagnet``, or ``Dipole``. Defaults to ``None``.
///
/// Examples:
///
///     .. code-block:: python
///
///         from pymagba.magnets import CylinderMagnet, CuboidMagnet, SourceCollection
///         import numpy as np
///
///         m1 = CylinderMagnet(
///             position=[0.005, 0.0, 0.0],
///             diameter=0.01,
///             height=0.02,
///             polarization=[0.0, 0.0, 1.0],
///         )
///         m2 = CuboidMagnet(
///             position=[-0.005, 0.0, 0.0],
///             dimensions=[0.01, 0.01, 0.01],
///             polarization=[0.0, 0.0, -1.0],
///         )
///         collection = SourceCollection([m1, m2])
///         points = np.array([[0.0, 0.0, 0.05]])
///         B = collection.compute_B(points)  # shape (1, 3)
#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct SourceCollection {
    pub(crate) inner: SourceAssembly<f64>,
}

#[pymethods]
impl SourceCollection {
    #[new]
    #[pyo3(signature = (sources=None))]
    fn new(sources: Option<Vec<Py<PyAny>>>, py: Python<'_>) -> PyResult<Self> {
        let mut components: Vec<SourceComponent<f64>> = Vec::new();

        if let Some(srcs) = sources {
            for src in &srcs {
                if let Ok(m) = src.extract::<PyRef<'_, CylinderMagnet>>(py) {
                    components.push(m.inner.clone().into());
                } else if let Ok(m) = src.extract::<PyRef<'_, CuboidMagnet>>(py) {
                    components.push(m.inner.clone().into());
                } else if let Ok(m) = src.extract::<PyRef<'_, Dipole>>(py) {
                    components.push(m.inner.clone().into());
                } else {
                    return Err(pyo3::exceptions::PyTypeError::new_err(
                        "sources must be CylinderMagnet, CuboidMagnet, or Dipole",
                    ));
                }
            }
        }

        Ok(Self {
            inner: SourceAssembly::from(components),
        })
    }
}

impl_pypose!(SourceCollection);
impl_compute_B!(SourceCollection);
