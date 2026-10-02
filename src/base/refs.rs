/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::collections::{SourceAssembly, SourceComponent};
use pyo3::prelude::*;

pub enum ObserverRef<'py> {
    Linear(PyRef<'py, crate::sensors::LinearHallSensor>),
    Switch(PyRef<'py, crate::sensors::HallSwitch>),
    Latch(PyRef<'py, crate::sensors::HallLatch>),
}

impl<'py> ObserverRef<'py> {
    pub fn try_extract(obj: &Bound<'py, PyAny>) -> PyResult<Self> {
        super::try_extract!(
            obj,
            Linear => crate::sensors::LinearHallSensor,
            Switch => crate::sensors::HallSwitch,
            Latch => crate::sensors::HallLatch,
        );
        Err(pyo3::exceptions::PyTypeError::new_err(
            "sensors must be LinearHallSensor, HallSwitch, or HallLatch",
        ))
    }

    pub fn try_extract_with_py(obj: &Py<PyAny>, py: Python<'py>) -> PyResult<Self> {
        Self::try_extract(obj.bind(py))
    }

    pub fn pose(&self) -> magba::base::Pose<f64> {
        match self {
            ObserverRef::Linear(s) => *s.inner.pose(),
            ObserverRef::Switch(s) => *s.inner.pose(),
            ObserverRef::Latch(s) => *s.inner.pose(),
        }
    }

    pub fn read_at_isometry(
        &self,
        eff_isometry: &nalgebra::Isometry3<f64>,
        source: &dyn magba::base::Source<f64>,
    ) -> magba::base::SensorOutput<f64> {
        use magba::base::Observer;
        match self {
            ObserverRef::Linear(s) => {
                let mut temp = s.inner.clone();
                temp.set_pose((*eff_isometry).into());
                temp.read(source)
            }
            ObserverRef::Switch(s) => {
                let mut temp = s.inner.clone();
                temp.set_pose((*eff_isometry).into());
                temp.read(source)
            }
            ObserverRef::Latch(s) => {
                let mut temp = s.inner.clone();
                temp.set_pose((*eff_isometry).into());
                let out = temp.read(source);
                let current_state = temp.state().load(std::sync::atomic::Ordering::SeqCst);
                s.inner
                    .state()
                    .store(current_state, std::sync::atomic::Ordering::SeqCst);
                out
            }
        }
    }
}

pub enum SourceRef<'py> {
    Cylinder(PyRef<'py, crate::magnets::CylinderMagnet>),
    Cuboid(PyRef<'py, crate::magnets::CuboidMagnet>),
    Dipole(PyRef<'py, crate::magnets::Dipole>),
    Sphere(PyRef<'py, crate::magnets::SphereMagnet>),
    TriangleMagnet(PyRef<'py, crate::magnets::TriangleMagnet>),
    TetrahedronMagnet(PyRef<'py, crate::magnets::TetrahedronMagnet>),
    MeshMagnet(PyRef<'py, crate::magnets::MeshMagnet>),
    CircularCurrent(PyRef<'py, crate::currents::CircularCurrent>),
    PathCurrent(PyRef<'py, crate::currents::PathCurrent>),
    TriangleCurrent(PyRef<'py, crate::currents::TriangleCurrent>),
    SheetCurrent(PyRef<'py, crate::currents::SheetCurrent>),
    Collection(PyRef<'py, crate::SourceCollection>, SourceAssembly<f64>),
}

impl<'py> SourceRef<'py> {
    pub fn try_extract(obj: &Bound<'py, PyAny>) -> PyResult<Self> {
        let py = obj.py();
        if obj.is_exact_instance_of::<crate::SourceCollection>() {
            let col = obj.extract::<PyRef<'py, crate::SourceCollection>>()?;
            let assembly = col.sync_assembly(py)?;
            return Ok(SourceRef::Collection(col, assembly));
        }
        super::try_extract!(
            obj,
            Cylinder => crate::magnets::CylinderMagnet,
            Cuboid => crate::magnets::CuboidMagnet,
            Dipole => crate::magnets::Dipole,
            Sphere => crate::magnets::SphereMagnet,
            TriangleMagnet => crate::magnets::TriangleMagnet,
            TetrahedronMagnet => crate::magnets::TetrahedronMagnet,
            MeshMagnet => crate::magnets::MeshMagnet,
            CircularCurrent => crate::currents::CircularCurrent,
            PathCurrent => crate::currents::PathCurrent,
            TriangleCurrent => crate::currents::TriangleCurrent,
            SheetCurrent => crate::currents::SheetCurrent,
        );
        if let Ok(col) = obj.extract::<PyRef<'py, crate::SourceCollection>>() {
            let assembly = col.sync_assembly(py)?;
            return Ok(SourceRef::Collection(col, assembly));
        }
        Err(pyo3::exceptions::PyTypeError::new_err(
            "source must be a valid Magnet, Current, or SourceCollection",
        ))
    }

    pub fn try_extract_with_py(obj: &Py<PyAny>, py: Python<'py>) -> PyResult<Self> {
        Self::try_extract(obj.bind(py))
    }

    pub fn pose(&self) -> magba::base::Pose<f64> {
        use magba::base::Transform;
        match self {
            SourceRef::Cylinder(m) => *m.inner.pose(),
            SourceRef::Cuboid(m) => *m.inner.pose(),
            SourceRef::Dipole(m) => *m.inner.pose(),
            SourceRef::Sphere(m) => *m.inner.pose(),
            SourceRef::TriangleMagnet(m) => *m.inner.pose(),
            SourceRef::TetrahedronMagnet(m) => *m.inner.pose(),
            SourceRef::MeshMagnet(m) => *m.inner.pose(),
            SourceRef::CircularCurrent(m) => *m.inner.pose(),
            SourceRef::PathCurrent(m) => *m.inner.pose(),
            SourceRef::TriangleCurrent(m) => *m.inner.pose(),
            SourceRef::SheetCurrent(m) => *m.inner.pose(),
            SourceRef::Collection(col, _) => col.inner,
        }
    }

    pub fn into_component(self) -> SourceComponent<f64> {
        match self {
            SourceRef::Cylinder(m) => m.inner.clone().into(),
            SourceRef::Cuboid(m) => m.inner.clone().into(),
            SourceRef::Dipole(m) => m.inner.clone().into(),
            SourceRef::Sphere(m) => m.inner.clone().into(),
            SourceRef::TriangleMagnet(m) => m.inner.clone().into(),
            SourceRef::TetrahedronMagnet(m) => m.inner.clone().into(),
            SourceRef::MeshMagnet(m) => m.inner.clone().into(),
            SourceRef::CircularCurrent(m) => m.inner.clone().into(),
            SourceRef::PathCurrent(m) => m.inner.clone().into(),
            SourceRef::TriangleCurrent(m) => m.inner.clone().into(),
            SourceRef::SheetCurrent(m) => m.inner.clone().into(),
            SourceRef::Collection(_, assembly) => SourceComponent::Assembly(assembly),
        }
    }

    pub fn as_source(&self) -> &dyn magba::base::Source<f64> {
        match self {
            SourceRef::Cylinder(m) => &m.inner,
            SourceRef::Cuboid(m) => &m.inner,
            SourceRef::Dipole(m) => &m.inner,
            SourceRef::Sphere(m) => &m.inner,
            SourceRef::TriangleMagnet(m) => &m.inner,
            SourceRef::TetrahedronMagnet(m) => &m.inner,
            SourceRef::MeshMagnet(m) => &m.inner,
            SourceRef::CircularCurrent(m) => &m.inner,
            SourceRef::PathCurrent(m) => &m.inner,
            SourceRef::TriangleCurrent(m) => &m.inner,
            SourceRef::SheetCurrent(m) => &m.inner,
            SourceRef::Collection(_, assembly) => assembly,
        }
    }
}
