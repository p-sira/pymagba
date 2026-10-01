/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::collections::SourceAssembly;
use numpy::PyArray1;
use pyo3::exceptions::PyIndexError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::IntoPyObject;

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::base::{try_into_quat, try_into_slice};
use crate::{
    base::{ObserverRef, SourceRef},
    macros::impl_pypose,
};

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass)]
pub struct SourceCollection {
    pub(crate) inner: magba::base::Pose<f64>,
    pub(crate) sources: Vec<Py<PyAny>>,
    pub(crate) local_offsets: Vec<nalgebra::Isometry3<f64>>,
}

impl SourceCollection {
    pub(crate) fn sync_assembly(&self, py: Python<'_>) -> PyResult<SourceAssembly<f64>> {
        use magba::base::Transform;
        let mut components = Vec::with_capacity(self.sources.len());
        for (src, local_offset) in self.sources.iter().zip(&self.local_offsets) {
            let s_ref = SourceRef::try_extract_with_py(src, py)?;
            let mut comp = s_ref.into_component();
            let eff_iso = self.inner.as_isometry() * local_offset;
            comp.set_pose(eff_iso.into());
            components.push(comp);
        }
        Ok(SourceAssembly::new(
            self.inner.position(),
            self.inner.orientation(),
            components,
        ))
    }
}

#[cfg_attr(feature = "stub-gen", gen_stub_pymethods)]
#[pymethods]
impl SourceCollection {
    #[new]
    #[pyo3(signature = (sources=None, position=None, orientation=None))]
    fn new(
        sources: Option<Vec<Py<PyAny>>>,
        position: Option<crate::base::ArrayLike3>,
        orientation: Option<crate::base::PyRotation>,
        py: Python<'_>,
    ) -> PyResult<Self> {
        let srcs = sources.unwrap_or_default();
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        let pose = magba::base::Pose::new(pos, rot);
        let parent_inv = pose.as_isometry().inverse();

        let mut local_offsets = Vec::with_capacity(srcs.len());
        for src in &srcs {
            let s_ref = SourceRef::try_extract_with_py(src, py)?;
            let child_pose = s_ref.pose();
            let local_offset = parent_inv * child_pose.as_isometry();
            local_offsets.push(local_offset);
        }

        Ok(Self {
            inner: pose,
            sources: srcs,
            local_offsets,
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
        let child_pose = s_ref.pose();
        let local_offset = self.inner.as_isometry().inverse() * child_pose.as_isometry();
        self.local_offsets.push(local_offset);
        self.sources.push(source);
        Ok(())
    }

    #[pyo3(name = "compute_B")]
    fn compute_B<'py>(
        &self,
        py: pyo3::Python<'py>,
        points: crate::base::PointsLike,
    ) -> PyResult<pyo3::Bound<'py, numpy::PyArray2<f64>>> {
        use magba::base::Source;
        let assembly = self.sync_assembly(py)?;
        let pts = points.0;
        let b_field = assembly.compute_B_batch(&pts);
        Ok(crate::util::vec3_to_pyarray2(py, b_field))
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new(py);
        dict.set_item("_schema_version", 1)?;
        dict.set_item("sources", self.sources.as_slice())?;
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        let offsets: Vec<([f64; 3], [f64; 4])> = self
            .local_offsets
            .iter()
            .map(|iso| {
                (
                    <[f64; 3]>::from(iso.translation.vector),
                    <[f64; 4]>::from(iso.rotation.into_inner().coords),
                )
            })
            .collect();
        dict.set_item("local_offsets", offsets)?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, PyDict>, py: Python<'_>) -> PyResult<()> {
        let sources_item = state.get_item("sources")?.ok_or_else(|| {
            pyo3::exceptions::PyKeyError::new_err("missing 'sources' in state")
        })?;
        let sources: Vec<Py<PyAny>> = sources_item.extract()?;

        let pos_item = state.get_item("position")?.ok_or_else(|| {
            pyo3::exceptions::PyKeyError::new_err("missing 'position' in state")
        })?;
        let position: [f64; 3] = pos_item.extract()?;

        let ori_item = state.get_item("orientation")?.ok_or_else(|| {
            pyo3::exceptions::PyKeyError::new_err("missing 'orientation' in state")
        })?;
        let orientation: [f64; 4] = ori_item.extract()?;

        let rot = crate::base::validate_and_normalize_quaternion(orientation)?;
        let pose = magba::base::Pose::new(position, rot);

        let local_offsets: Vec<nalgebra::Isometry3<f64>> = if let Ok(Some(offsets_item)) =
            state.get_item("local_offsets")
        {
            let raw: Vec<([f64; 3], [f64; 4])> = offsets_item.extract()?;
            let mut offsets = Vec::with_capacity(raw.len());
            for (t, r) in raw {
                let r_rot = crate::base::validate_and_normalize_quaternion(r)?;
                offsets.push(nalgebra::Isometry3::from_parts(
                    nalgebra::Translation3::from(t),
                    r_rot,
                ));
            }
            offsets
        } else {
            // Legacy unversioned state compatibility:
            let mut offsets = Vec::with_capacity(sources.len());
            for s in &sources {
                if let Ok(s_ref) = SourceRef::try_extract_with_py(s, py) {
                    offsets.push(*s_ref.pose().as_isometry());
                } else {
                    offsets.push(nalgebra::Isometry3::identity());
                }
            }
            offsets
        };

        self.inner = pose;
        self.sources = sources;
        self.local_offsets = local_offsets;
        Ok(())
    }
}

impl_pypose!(SourceCollection);

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass)]
pub struct ObserverCollection {
    pub(crate) inner: magba::base::Pose<f64>,
    pub(crate) sensors: Vec<Py<PyAny>>,
    pub(crate) local_offsets: Vec<nalgebra::Isometry3<f64>>,
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
        let pos = try_into_slice!(position);
        let rot = try_into_quat!(orientation);
        let pose = magba::base::Pose::new(pos, rot);
        let parent_inv = pose.as_isometry().inverse();

        let mut local_offsets = Vec::with_capacity(sens.len());
        for s in &sens {
            let o_ref = ObserverRef::try_extract_with_py(s, py)?;
            let child_pose = o_ref.pose();
            let local_offset = parent_inv * child_pose.as_isometry();
            local_offsets.push(local_offset);
        }

        Ok(Self {
            inner: pose,
            sensors: sens,
            local_offsets,
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
        let child_pose = o_ref.pose();
        let local_offset = self.inner.as_isometry().inverse() * child_pose.as_isometry();
        self.local_offsets.push(local_offset);
        self.sensors.push(sensor);
        Ok(())
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new(py);
        dict.set_item("_schema_version", 1)?;
        dict.set_item("sensors", self.sensors.as_slice())?;
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        let offsets: Vec<([f64; 3], [f64; 4])> = self
            .local_offsets
            .iter()
            .map(|iso| {
                (
                    <[f64; 3]>::from(iso.translation.vector),
                    <[f64; 4]>::from(iso.rotation.into_inner().coords),
                )
            })
            .collect();
        dict.set_item("local_offsets", offsets)?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, PyDict>, py: Python<'_>) -> PyResult<()> {
        let sensors_item = state.get_item("sensors")?.ok_or_else(|| {
            pyo3::exceptions::PyKeyError::new_err("missing 'sensors' in state")
        })?;
        let sensors: Vec<Py<PyAny>> = sensors_item.extract()?;

        let pos_item = state.get_item("position")?.ok_or_else(|| {
            pyo3::exceptions::PyKeyError::new_err("missing 'position' in state")
        })?;
        let position: [f64; 3] = pos_item.extract()?;

        let ori_item = state.get_item("orientation")?.ok_or_else(|| {
            pyo3::exceptions::PyKeyError::new_err("missing 'orientation' in state")
        })?;
        let orientation: [f64; 4] = ori_item.extract()?;

        let rot = crate::base::validate_and_normalize_quaternion(orientation)?;
        let pose = magba::base::Pose::new(position, rot);

        let local_offsets: Vec<nalgebra::Isometry3<f64>> = if let Ok(Some(offsets_item)) =
            state.get_item("local_offsets")
        {
            let raw: Vec<([f64; 3], [f64; 4])> = offsets_item.extract()?;
            let mut offsets = Vec::with_capacity(raw.len());
            for (t, r) in raw {
                let r_rot = crate::base::validate_and_normalize_quaternion(r)?;
                offsets.push(nalgebra::Isometry3::from_parts(
                    nalgebra::Translation3::from(t),
                    r_rot,
                ));
            }
            offsets
        } else {
            // Legacy unversioned state compatibility:
            let mut offsets = Vec::with_capacity(sensors.len());
            for s in &sensors {
                if let Ok(o_ref) = ObserverRef::try_extract_with_py(s, py) {
                    offsets.push(*o_ref.pose().as_isometry());
                } else {
                    offsets.push(nalgebra::Isometry3::identity());
                }
            }
            offsets
        };

        self.inner = pose;
        self.sensors = sensors;
        self.local_offsets = local_offsets;
        Ok(())
    }

    fn read_all(&self, source: Bound<'_, PyAny>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let s_ref = SourceRef::try_extract(&source)?;
        let list = PyList::empty(py);
        for (sensor_py, local_offset) in self.sensors.iter().zip(&self.local_offsets) {
            let o_ref = ObserverRef::try_extract_with_py(sensor_py, py)?;
            let eff_isometry = self.inner.as_isometry() * local_offset;
            let output = o_ref.read_at_isometry(&eff_isometry, s_ref.as_source());
            list.append(sensor_output_to_py(py, output)?)?;
        }
        Ok(list.into_any().unbind())
    }
}

impl_pypose!(ObserverCollection);

fn sensor_output_to_py(
    py: Python<'_>,
    output: magba::base::SensorOutput<f64>,
) -> PyResult<Py<PyAny>> {
    match output {
        magba::base::SensorOutput::Scalar(val) => {
            Ok(val.into_pyobject(py)?.into_any().unbind())
        }
        magba::base::SensorOutput::Vector(vec) => {
            Ok(PyArray1::from_slice(py, &[vec.x, vec.y, vec.z])
                .into_any()
                .unbind())
        }
        magba::base::SensorOutput::Digital(val) => {
            let b = val != 0;
            Ok(b.into_pyobject(py)?.to_owned().into_any().into())
        }
    }
}
