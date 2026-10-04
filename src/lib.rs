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

#[cfg(feature = "threshold-calibration")]
mod execution;

#[macro_use]
mod macros;

use collection::{ObserverCollection, SourceCollection};
use currents::*;
use magnets::*;
use sensors::*;

#[cfg(feature = "stub-gen")]
pyo3_stub_gen::define_stub_info_gatherer!(stub_info);

#[pymodule(gil_used = false)]
fn pymagba_binding(m: Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SourceCollection>()?;
    m.add_class::<CylinderMagnet>()?;
    m.add_class::<CuboidMagnet>()?;
    m.add_class::<SphereMagnet>()?;
    m.add_class::<Dipole>()?;
    m.add_class::<TriangleMagnet>()?;
    m.add_class::<TetrahedronMagnet>()?;
    m.add_class::<MeshMagnet>()?;
    m.add_class::<CircularCurrent>()?;
    m.add_class::<PathCurrent>()?;
    m.add_class::<TriangleCurrent>()?;
    m.add_class::<SheetCurrent>()?;
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
    magnets.add_class::<TriangleMagnet>()?;
    magnets.add_class::<TetrahedronMagnet>()?;
    magnets.add_class::<MeshMagnet>()?;
    magnets.add_class::<SourceCollection>()?;
    m.add_submodule(&magnets)?;

    let currents = PyModule::new(py, "currents")?;
    currents.add_class::<CircularCurrent>()?;
    currents.add_class::<PathCurrent>()?;
    currents.add_class::<TriangleCurrent>()?;
    currents.add_class::<SheetCurrent>()?;
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
    m.add_function(wrap_pyfunction!(fields::triangle_B, &m)?)?;
    m.add_function(wrap_pyfunction!(fields::tetrahedron_B, &m)?)?;
    m.add_function(wrap_pyfunction!(fields::mesh_B, &m)?)?;
    m.add_function(wrap_pyfunction!(fields::path_current_B, &m)?)?;
    m.add_function(wrap_pyfunction!(fields::triangle_current_B, &m)?)?;
    m.add_function(wrap_pyfunction!(fields::sheet_current_B, &m)?)?;

    #[cfg(feature = "threshold-calibration")]
    {
        m.add_function(wrap_pyfunction!(_set_threshold_calibration, &m)?)?;
        m.add_function(wrap_pyfunction!(_threshold_calibration_state, &m)?)?;
    }

    let fields_mod = PyModule::new(m.py(), "fields")?;
    fields::fields(&fields_mod)?;
    m.add_submodule(&fields_mod)?;

    Ok(())
}

#[cfg(feature = "threshold-calibration")]
#[pyfunction]
#[pyo3(signature = (rust_mode="auto", gil_mode="auto", instrument=false))]
fn _set_threshold_calibration(rust_mode: &str, gil_mode: &str, instrument: bool) -> PyResult<()> {
    use execution::GilMode;
    use magba::threshold_calibration::ExecutionMode;

    let rust_mode = match rust_mode {
        "auto" => ExecutionMode::Auto,
        "serial" => ExecutionMode::Serial,
        "parallel" => ExecutionMode::Parallel,
        value => {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "invalid Rust execution mode {value:?}; expected auto, serial, or parallel"
            )))
        }
    };
    let gil_mode = match gil_mode {
        "auto" => GilMode::Auto,
        "retain" => GilMode::Retain,
        "detach" => GilMode::Detach,
        value => {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "invalid GIL mode {value:?}; expected auto, retain, or detach"
            )))
        }
    };

    magba::threshold_calibration::set_execution_mode(rust_mode);
    magba::threshold_calibration::set_instrumentation(instrument);
    magba::threshold_calibration::reset_branch_counts();
    execution::set_gil_mode(gil_mode);
    execution::set_instrumentation(instrument);
    execution::reset_branch_counts();
    Ok(())
}

#[cfg(feature = "threshold-calibration")]
#[pyfunction]
fn _threshold_calibration_state(py: Python<'_>) -> PyResult<Py<PyAny>> {
    use pyo3::types::PyDict;

    let state = PyDict::new(py);
    state.set_item(
        "rust_mode",
        format!("{:?}", magba::threshold_calibration::execution_mode()).to_lowercase(),
    )?;
    state.set_item(
        "gil_mode",
        format!("{:?}", execution::gil_mode()).to_lowercase(),
    )?;
    state.set_item("instrument", execution::instrumentation())?;
    state.set_item(
        "rust_branches",
        magba::threshold_calibration::branch_counts(),
    )?;
    state.set_item("gil_branches", execution::branch_counts())?;
    Ok(state.into_any().unbind())
}
