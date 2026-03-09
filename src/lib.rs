/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

#![allow(non_snake_case)]

use pyo3::prelude::*;

mod base;
mod util;

mod collection;
mod currents;
mod fields;
mod magnets;
mod sensors;

#[macro_use]
mod macros;

use collection::{ObserverCollection, SourceCollection};
use currents::*;
use magnets::*;
use sensors::*;

pyo3_stub_gen::define_stub_info_gatherer!(stub_info);

#[pymodule(gil_used = false)]
fn pymagba_binding(m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SourceCollection>()?;
    m.add_class::<CylinderMagnet>()?;
    m.add_class::<CuboidMagnet>()?;
    m.add_class::<SphereMagnet>()?;
    m.add_class::<Dipole>()?;
    m.add_class::<CircularCurrent>()?;
    m.add_class::<ObserverCollection>()?;
    m.add_class::<LinearHallSensor>()?;
    m.add_class::<HallSwitch>()?;
    m.add_class::<HallLatch>()?;

    let py = m.py();

    let magnets = PyModule::new(py, "magnets")?;
    magnets.add_class::<CylinderMagnet>()?;
    magnets.add_class::<CuboidMagnet>()?;
    magnets.add_class::<SphereMagnet>()?;
    magnets.add_class::<Dipole>()?;
    magnets.add_class::<SourceCollection>()?;
    m.add_submodule(&magnets)?;

    let currents = PyModule::new(py, "currents")?;
    currents.add_class::<CircularCurrent>()?;
    currents.add_class::<SourceCollection>()?;
    m.add_submodule(&currents)?;

    let sensors = PyModule::new(py, "sensors")?;
    sensors.add_class::<LinearHallSensor>()?;
    sensors.add_class::<HallSwitch>()?;
    sensors.add_class::<HallLatch>()?;
    sensors.add_class::<ObserverCollection>()?;
    m.add_submodule(&sensors)?;

    m.add_function(wrap_pyfunction!(fields::cylinder_B, &m)?)?;
    m.add_function(wrap_pyfunction!(fields::dipole_B, &m)?)?;
    m.add_function(wrap_pyfunction!(fields::cuboid_B, &m)?)?;
    m.add_function(wrap_pyfunction!(fields::sphere_B, &m)?)?;
    m.add_function(wrap_pyfunction!(fields::circular_B, &m)?)?;

    let fields_mod = PyModule::new(m.py(), "fields")?;
    fields::fields(&fields_mod)?;
    m.add_submodule(&fields_mod)?;

    Ok(())
}
