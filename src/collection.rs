/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use std::collections::HashSet;

use magba::collections::SourceAssembly;
use numpy::PyArray1;
use pyo3::exceptions::{PyIndexError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use pyo3::{IntoPyObject, PyTraverseError, PyVisit};

#[cfg(feature = "stub-gen")]
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

use crate::base::{get_state_item, try_into_quat, try_into_slice};
use crate::{
    base::{ObserverRef, SourceRef},
    macros::impl_pypose,
};

fn check_cycle_containment(
    root: &Bound<'_, PyAny>,
    target: *mut pyo3::ffi::PyObject,
    visited: &mut HashSet<*mut pyo3::ffi::PyObject>,
    on_stack: &mut HashSet<*mut pyo3::ffi::PyObject>,
) -> PyResult<bool> {
    let ptr = root.as_ptr();
    if !target.is_null() && ptr == target {
        return Ok(true);
    }
    if on_stack.contains(&ptr) {
        return Ok(true);
    }
    if visited.contains(&ptr) {
        return Ok(false);
    }

    on_stack.insert(ptr);

    if let Ok(col) = root.extract::<PyRef<'_, SourceCollection>>() {
        for child_py in &col.sources {
            let child = child_py.bind(root.py());
            if check_cycle_containment(child, target, visited, on_stack)? {
                return Ok(true);
            }
        }
    }

    on_stack.remove(&ptr);
    visited.insert(ptr);
    Ok(false)
}

pub(crate) struct CachedAssembly {
    parent_pose: magba::base::Pose<f64>,
    child_fingerprints: Vec<u64>,
    assembly: std::sync::Arc<SourceAssembly<f64>>,
}

fn poses_equal(p1: &magba::base::Pose<f64>, p2: &magba::base::Pose<f64>) -> bool {
    p1.position() == p2.position() && p1.orientation() == p2.orientation()
}

#[cfg_attr(feature = "stub-gen", gen_stub_pyclass)]
#[pyclass(module = "pymagba.pymagba_binding", subclass)]
pub struct SourceCollection {
    pub(crate) inner: magba::base::Pose<f64>,
    pub(crate) sources: Vec<Py<PyAny>>,
    pub(crate) local_offsets: Vec<nalgebra::Isometry3<f64>>,
    pub(crate) cached: std::sync::Mutex<Option<CachedAssembly>>,
}

impl SourceCollection {
    pub(crate) fn get_or_sync_assembly(
        &self,
        py: Python<'_>,
    ) -> PyResult<std::sync::Arc<SourceAssembly<f64>>> {
        use magba::base::Transform;

        let mut guard = self.cached.lock().unwrap();

        if let Some(ref mut c) = *guard {
            if c.child_fingerprints.len() == self.sources.len() {
                let mut all_match = true;
                for (src, &expected_fp) in self.sources.iter().zip(&c.child_fingerprints) {
                    let s_ref = SourceRef::try_extract_with_py(src, py)?;
                    if s_ref.state_fingerprint(py) != expected_fp {
                        all_match = false;
                        break;
                    }
                }
                if all_match {
                    if poses_equal(&c.parent_pose, &self.inner) {
                        return Ok(c.assembly.clone());
                    } else {
                        let assembly_mut = std::sync::Arc::make_mut(&mut c.assembly);
                        assembly_mut.set_pose(self.inner);
                        c.parent_pose = self.inner;
                        return Ok(c.assembly.clone());
                    }
                }
            }
        }

        // Cache miss or child mismatch: rebuild components and fingerprints
        let mut components = Vec::with_capacity(self.sources.len());
        let mut fingerprints = Vec::with_capacity(self.sources.len());
        for (src, local_offset) in self.sources.iter().zip(&self.local_offsets) {
            let s_ref = SourceRef::try_extract_with_py(src, py)?;
            fingerprints.push(s_ref.state_fingerprint(py));
            let mut comp = s_ref.into_component();
            let eff_iso = self.inner.as_isometry() * local_offset;
            comp.set_pose(eff_iso.into());
            components.push(comp);
        }

        let assembly = std::sync::Arc::new(SourceAssembly::new(
            self.inner.position(),
            self.inner.orientation(),
            components,
        ));

        *guard = Some(CachedAssembly {
            parent_pose: self.inner,
            child_fingerprints: fingerprints,
            assembly: assembly.clone(),
        });

        Ok(assembly)
    }

    #[allow(dead_code)]
    pub(crate) fn sync_assembly(&self, py: Python<'_>) -> PyResult<SourceAssembly<f64>> {
        self.get_or_sync_assembly(py).map(|a| (*a).clone())
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
        let mut visited = HashSet::new();
        let mut on_stack = HashSet::new();
        for src in &srcs {
            let bound = src.bind(py);
            if check_cycle_containment(bound, std::ptr::null_mut(), &mut visited, &mut on_stack)? {
                return Err(PyValueError::new_err(
                    "Cannot create a collection with a circular collection hierarchy",
                ));
            }
        }

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
            cached: std::sync::Mutex::new(None),
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

    fn append(slf: &Bound<'_, Self>, source: Py<PyAny>, py: Python<'_>) -> PyResult<()> {
        let target = slf.as_ptr();
        let mut visited = HashSet::new();
        let mut on_stack = HashSet::new();
        let bound = source.bind(py);
        if check_cycle_containment(bound, target, &mut visited, &mut on_stack)? {
            return Err(PyValueError::new_err(
                "Cannot add collection to itself or create a circular collection hierarchy",
            ));
        }

        let s_ref = SourceRef::try_extract_with_py(&source, py)?;
        let child_pose = s_ref.pose();
        let mut inner = slf.borrow_mut();
        inner.cached.lock().unwrap().take();
        let local_offset = inner.inner.as_isometry().inverse() * child_pose.as_isometry();
        inner.local_offsets.push(local_offset);
        inner.sources.push(source);
        Ok(())
    }

    #[pyo3(name = "compute_B")]
    fn compute_B<'py>(
        &self,
        py: pyo3::Python<'py>,
        points: crate::base::PointsLike<'py>,
    ) -> PyResult<pyo3::Bound<'py, numpy::PyArray2<f64>>> {
        use magba::base::Source;
        let assembly = self.get_or_sync_assembly(py)?;
        let pts = points.as_slice();
        #[cfg(feature = "threshold-calibration")]
        let detach = crate::execution::should_detach(pts.len() > 1);
        #[cfg(not(feature = "threshold-calibration"))]
        let detach = pts.len() > 1;

        let b_field = if detach {
            py.detach(|| assembly.compute_B_batch(pts))
        } else {
            assembly.compute_B_batch(pts)
        };
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

    fn __setstate__(
        slf: &Bound<'_, Self>,
        state: Bound<'_, PyDict>,
        py: Python<'_>,
    ) -> PyResult<()> {
        let sources: Vec<Py<PyAny>> = get_state_item!(state, "sources", Vec<Py<PyAny>>)?;
        let target = slf.as_ptr();
        let mut visited = HashSet::new();
        let mut on_stack = HashSet::new();
        for s in &sources {
            let bound = s.bind(py);
            if check_cycle_containment(bound, target, &mut visited, &mut on_stack)? {
                return Err(PyValueError::new_err(
                    "Cannot restore collection with a circular collection hierarchy",
                ));
            }
        }

        for s in &sources {
            SourceRef::try_extract_with_py(s, py)?;
        }

        let position: [f64; 3] = get_state_item!(state, "position", [f64; 3])?;
        let orientation: [f64; 4] = get_state_item!(state, "orientation", [f64; 4])?;

        let rot = crate::base::validate_and_normalize_quaternion(orientation)?;
        let pose = magba::base::Pose::new(position, rot);

        let local_offsets: Vec<nalgebra::Isometry3<f64>> =
            if let Ok(Some(offsets_item)) = state.get_item("local_offsets") {
                let raw: Vec<([f64; 3], [f64; 4])> = offsets_item.extract()?;
                if raw.len() != sources.len() {
                    return Err(PyValueError::new_err(format!(
                        "Number of local_offsets ({}) does not match number of sources ({})",
                        raw.len(),
                        sources.len()
                    )));
                }
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
                    let s_ref = SourceRef::try_extract_with_py(s, py)?;
                    offsets.push(*s_ref.pose().as_isometry());
                }
                offsets
            };

        let mut inner = slf.borrow_mut();
        inner.cached.lock().unwrap().take();
        inner.inner = pose;
        inner.sources = sources;
        inner.local_offsets = local_offsets;
        Ok(())
    }
}

#[pymethods]
impl SourceCollection {
    fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        for s in &self.sources {
            visit.call(s)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.cached.lock().unwrap().take();
        self.sources.clear();
        self.local_offsets.clear();
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
        let sensors: Vec<Py<PyAny>> = get_state_item!(state, "sensors", Vec<Py<PyAny>>)?;
        for s in &sensors {
            ObserverRef::try_extract_with_py(s, py)?;
        }

        let position: [f64; 3] = get_state_item!(state, "position", [f64; 3])?;
        let orientation: [f64; 4] = get_state_item!(state, "orientation", [f64; 4])?;

        let rot = crate::base::validate_and_normalize_quaternion(orientation)?;
        let pose = magba::base::Pose::new(position, rot);

        let local_offsets: Vec<nalgebra::Isometry3<f64>> =
            if let Ok(Some(offsets_item)) = state.get_item("local_offsets") {
                let raw: Vec<([f64; 3], [f64; 4])> = offsets_item.extract()?;
                if raw.len() != sensors.len() {
                    return Err(pyo3::exceptions::PyValueError::new_err(format!(
                        "Number of local_offsets ({}) does not match number of sensors ({})",
                        raw.len(),
                        sensors.len()
                    )));
                }
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
                    let o_ref = ObserverRef::try_extract_with_py(s, py)?;
                    offsets.push(*o_ref.pose().as_isometry());
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

        #[cfg(feature = "threshold-calibration")]
        if crate::execution::should_detach(false) {
            use magba::base::Observer;

            let owned_source = s_ref.into_component();
            for (sensor_py, local_offset) in self.sensors.iter().zip(&self.local_offsets) {
                let o_ref = ObserverRef::try_extract_with_py(sensor_py, py)?;
                let eff_isometry = self.inner.as_isometry() * local_offset;
                let staged = o_ref.staged_at_isometry(&eff_isometry);
                let (staged, output) = py.detach(|| {
                    let output = staged.read(&owned_source);
                    (staged, output)
                });
                o_ref.sync_staged_state(&staged);
                list.append(sensor_output_to_py(py, output)?)?;
            }
            return Ok(list.into_any().unbind());
        }

        for (sensor_py, local_offset) in self.sensors.iter().zip(&self.local_offsets) {
            let o_ref = ObserverRef::try_extract_with_py(sensor_py, py)?;
            let eff_isometry = self.inner.as_isometry() * local_offset;
            let output = o_ref.read_at_isometry(&eff_isometry, s_ref.as_source());
            list.append(sensor_output_to_py(py, output)?)?;
        }
        Ok(list.into_any().unbind())
    }
}

#[pymethods]
impl ObserverCollection {
    fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        for s in &self.sensors {
            visit.call(s)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.sensors.clear();
        self.local_offsets.clear();
    }
}

impl_pypose!(ObserverCollection);

fn sensor_output_to_py(
    py: Python<'_>,
    output: magba::base::SensorOutput<f64>,
) -> PyResult<Py<PyAny>> {
    match output {
        magba::base::SensorOutput::Scalar(val) => Ok(val.into_pyobject(py)?.into_any().unbind()),
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
