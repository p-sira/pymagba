/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use magba::collections::{ObserverComponent, SourceComponent};
use pyo3::prelude::*;

#[derive(FromPyObject)]
pub enum ObserverRef<'py> {
    Linear(PyRef<'py, crate::sensors::LinearHallSensor>),
    Switch(PyRef<'py, crate::sensors::HallSwitch>),
    Latch(PyRef<'py, crate::sensors::HallLatch>),
}

impl<'py> ObserverRef<'py> {
    pub fn try_extract(obj: &Bound<'py, PyAny>) -> PyResult<Self> {
        obj.extract::<Self>().map_err(|_| {
            pyo3::exceptions::PyTypeError::new_err(
                "sensors must be LinearHallSensor, HallSwitch, or HallLatch",
            )
        })
    }

    pub fn try_extract_with_py(obj: &Py<PyAny>, py: Python<'py>) -> PyResult<Self> {
        Self::try_extract(obj.bind(py))
    }

    pub fn into_component(self) -> ObserverComponent<f64> {
        match self {
            ObserverRef::Linear(s) => s.inner.clone().into(),
            ObserverRef::Switch(s) => s.inner.clone().into(),
            ObserverRef::Latch(s) => s.inner.clone().into(),
        }
    }
}

#[derive(FromPyObject)]
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
    Collection(PyRef<'py, crate::SourceCollection>),
}

impl<'py> SourceRef<'py> {
    pub fn try_extract(obj: &Bound<'py, PyAny>) -> PyResult<Self> {
        obj.extract::<Self>().map_err(|_| {
            pyo3::exceptions::PyTypeError::new_err(
                "source must be a valid Magnet, Current, or SourceCollection",
            )
        })
    }

    pub fn try_extract_with_py(obj: &Py<PyAny>, py: Python<'py>) -> PyResult<Self> {
        Self::try_extract(obj.bind(py))
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
            SourceRef::Collection(m) => m.inner.clone().into(),
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
            SourceRef::Collection(m) => &m.inner,
        }
    }
}
