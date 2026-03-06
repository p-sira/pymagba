/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use pyo3::prelude::*;

mod collection;
mod magnets;
mod sensors;
mod util;

#[macro_use]
mod macros;

use collection::SourceCollection;
use magnets::*;
use sensors::*;

#[pymodule(gil_used = false)]
#[pyo3(name = "pymagba_binding")]
fn pymagba_binding(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SourceCollection>()?;
    m.add_class::<CylinderMagnet>()?;
    m.add_class::<CuboidMagnet>()?;
    m.add_class::<Dipole>()?;
    m.add_class::<LinearHallSensor>()?;
    m.add_class::<HallSwitch>()?;
    m.add_class::<HallLatch>()?;

    let magnets = PyModule::new(py, "magnets")?;
    magnets.add_class::<CylinderMagnet>()?;
    magnets.add_class::<CuboidMagnet>()?;
    magnets.add_class::<Dipole>()?;
    m.add_submodule(&magnets)?;

    let sensors = PyModule::new(py, "sensors")?;
    sensors.add_class::<LinearHallSensor>()?;
    sensors.add_class::<HallSwitch>()?;
    sensors.add_class::<HallLatch>()?;
    m.add_submodule(&sensors)?;

    Ok(())
}
