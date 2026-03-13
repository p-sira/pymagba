/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use std::sync::Arc;

use magba::collections::{ObserverAssembly, ObserverComponent, SourceAssembly, SourceComponent};
use nalgebra::UnitQuaternion;
use numpy::PyArray1;
use pyo3::exceptions::PyIndexError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::IntoPyObject;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::base::{extract_states, try_into_quat};
use crate::{
    base::{ObserverRef, SourceRef},
    macros::{impl_compute_B, impl_pypose},
};

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct SourceCollection {
    pub(crate) inner: SourceAssembly<f64>,
    pub(crate) sources: Arc<Vec<Py<PyAny>>>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl SourceCollection {
    #[new]
    #[pyo3(signature = (sources=None))]
    fn new(sources: Option<Vec<Py<PyAny>>>, py: Python<'_>) -> PyResult<Self> {
        let srcs = sources.unwrap_or_default();
        let mut components = Vec::with_capacity(srcs.len());

        for src in &srcs {
            let s_ref = SourceRef::try_extract_with_py(src, py)?;
            components.push(s_ref.into_component());
        }

        Ok(Self {
            inner: SourceAssembly::from(components),
            sources: Arc::new(srcs),
        })
    }

    fn __len__(&self) -> usize {
        self.sources.len()
    }

    fn __getitem__(&self, idx: isize, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let len = self.sources.len() as isize;
        let idx = if idx < 0 { len + idx } else { idx };
        if idx < 0 || idx >= len {
            return Err(PyIndexError::new_err("index out of range"));
        }
        Ok(self.sources[idx as usize].clone_ref(py))
    }

    fn append(&mut self, source: Py<PyAny>, py: Python<'_>) -> PyResult<()> {
        let s_ref = SourceRef::try_extract_with_py(&source, py)?;
        self.inner.push(s_ref.into_component());

        let mut new_sources: Vec<Py<PyAny>> =
            self.sources.iter().map(|s| s.clone_ref(py)).collect();
        new_sources.push(source);
        self.sources = Arc::new(new_sources);
        Ok(())
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new(py);
        dict.set_item("sources", self.sources.as_ref())?;
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, PyDict>, py: Python<'_>) -> PyResult<()> {
        let sources: Vec<Py<PyAny>> = state.get_item("sources")?.unwrap().extract()?;
        extract_states!(state, [position;3, orientation;4]);

        let mut components: Vec<SourceComponent<f64>> = Vec::with_capacity(sources.len());
        for src in sources.iter() {
            if let Ok(s_ref) = src.extract::<SourceRef>(py) {
                components.push(s_ref.into_component());
            }
        }

        self.inner = SourceAssembly::new(
            position.into(),
            UnitQuaternion::from_quaternion(orientation.into()),
            components,
        );
        self.sources = Arc::new(sources);
        Ok(())
    }
}

impl_pypose!(SourceCollection);
impl_compute_B!(SourceCollection);

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass, from_py_object)]
#[derive(Clone)]
pub struct ObserverCollection {
    pub(crate) inner: ObserverAssembly<f64>,
    pub(crate) sensors: Arc<Vec<Py<PyAny>>>,
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl ObserverCollection {
    #[new]
    #[pyo3(signature = (sensors=None, position=None, orientation=None))]
    fn new(
        sensors: Option<Vec<Py<PyAny>>>,
        position: Option<crate::base::ArrayLike3>,
        orientation: Option<crate::base::PyRotation>,
        py: Python<'_>,
    ) -> PyResult<Self> {
        let sens = sensors.unwrap_or_default();
        let mut components = Vec::with_capacity(sens.len());

        for s in &sens {
            let o_ref = ObserverRef::try_extract_with_py(s, py)?;
            components.push(o_ref.into_component());
        }

        let pos: nalgebra::Point3<f64> = position
            .map(|p| p.0.into())
            .unwrap_or_else(|| [0.0, 0.0, 0.0].into());
        let rot: nalgebra::UnitQuaternion<f64> = try_into_quat!(orientation);

        let mut inner = ObserverAssembly::from(components);
        inner.set_position(pos);
        inner.set_orientation(rot);

        Ok(Self {
            inner,
            sensors: Arc::new(sens),
        })
    }

    fn __len__(&self) -> usize {
        self.sensors.len()
    }

    fn __getitem__(&self, idx: isize, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let len = self.sensors.len() as isize;
        let idx = if idx < 0 { len + idx } else { idx };
        if idx < 0 || idx >= len {
            return Err(PyIndexError::new_err("index out of range"));
        }
        Ok(self.sensors[idx as usize].clone_ref(py))
    }

    fn append(&mut self, sensor: Py<PyAny>, py: Python<'_>) -> PyResult<()> {
        let o_ref = ObserverRef::try_extract_with_py(&sensor, py)?;
        self.inner.push(o_ref.into_component());

        let mut new_sensors: Vec<Py<PyAny>> =
            self.sensors.iter().map(|s| s.clone_ref(py)).collect();
        new_sensors.push(sensor);
        self.sensors = Arc::new(new_sensors);
        Ok(())
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new(py);
        dict.set_item("sensors", self.sensors.as_ref())?;
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, PyDict>, py: Python<'_>) -> PyResult<()> {
        let sensors: Vec<Py<PyAny>> = state.get_item("sensors")?.unwrap().extract()?;
        extract_states!(state, [position;3, orientation;4]);

        let mut components: Vec<ObserverComponent<f64>> = Vec::with_capacity(sensors.len());
        for src in sensors.iter() {
            if let Ok(s_ref) = src.extract::<ObserverRef>(py) {
                components.push(s_ref.into_component());
            }
        }

        self.inner = ObserverAssembly::new(
            position.into(),
            UnitQuaternion::from_quaternion(orientation.into()),
            components,
        );
        self.sensors = Arc::new(sensors);
        Ok(())
    }

    fn read_all(&self, source: Bound<'_, PyAny>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let s_ref = SourceRef::try_extract(&source)?;
        let results = self.inner.read_all(s_ref.as_source());

        let list = PyList::empty(py);
        for o in results {
            list.append(sensor_output_to_py(py, o))?;
        }
        Ok(list.into_any().unbind())
    }
}

impl_pypose!(ObserverCollection);

fn sensor_output_to_py(py: Python<'_>, output: magba::base::SensorOutput<f64>) -> Py<PyAny> {
    match output {
        magba::base::SensorOutput::Scalar(val) => {
            val.into_pyobject(py).unwrap().into_any().unbind()
        }
        magba::base::SensorOutput::Vector(vec) => PyArray1::from_slice(py, &[vec.x, vec.y, vec.z])
            .into_any()
            .unbind(),
        magba::base::SensorOutput::Digital(val) => {
            let b = val != 0;
            b.into_pyobject(py).unwrap().to_owned().into_any().into()
        }
    }
}
