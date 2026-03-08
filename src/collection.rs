/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::collections::{SourceAssembly, SourceComponent};
use pyo3::prelude::*;

use crate::{impl_compute_B, impl_pypose, magnets::*};

#[pyclass(subclass, from_py_object)]
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
