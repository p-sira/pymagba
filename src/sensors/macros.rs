/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

macro_rules! impl_read_voltage {
    ($Struct:ty) => {
        #[pyo3::pymethods]
        impl $Struct {
            fn read_voltage_cylinder(&self, source: &crate::magnets::CylinderMagnet) -> f64 {
                self.inner.read_voltage(&source.inner)
            }
            fn read_voltage_cuboid(&self, source: &crate::magnets::CuboidMagnet) -> f64 {
                self.inner.read_voltage(&source.inner)
            }
            fn read_voltage_dipole(&self, source: &crate::magnets::Dipole) -> f64 {
                self.inner.read_voltage(&source.inner)
            }
            fn read_voltage_collection(&self, source: &crate::collection::SourceCollection) -> f64 {
                self.inner.read_voltage(&source.inner)
            }

            fn read(&self, source: pyo3::Bound<'_, pyo3::PyAny>) -> pyo3::PyResult<f64> {
                if let Ok(m) = source.extract::<pyo3::PyRef<'_, crate::magnets::CylinderMagnet>>() {
                    Ok(self.read_voltage_cylinder(&m))
                } else if let Ok(m) =
                    source.extract::<pyo3::PyRef<'_, crate::magnets::CuboidMagnet>>()
                {
                    Ok(self.read_voltage_cuboid(&m))
                } else if let Ok(m) = source.extract::<pyo3::PyRef<'_, crate::magnets::Dipole>>() {
                    Ok(self.read_voltage_dipole(&m))
                } else if let Ok(m) =
                    source.extract::<pyo3::PyRef<'_, crate::collection::SourceCollection>>()
                {
                    Ok(self.read_voltage_collection(&m))
                } else {
                    Err(pyo3::exceptions::PyTypeError::new_err(
                        "source must be CylinderMagnet, CuboidMagnet, Dipole, or SourceCollection",
                    ))
                }
            }
        }
    };
}

macro_rules! impl_read_state {
    ($Struct:ty) => {
        #[pyo3::pymethods]
        impl $Struct {
            fn read_state_cylinder(&self, source: &crate::magnets::CylinderMagnet) -> bool {
                self.inner.read_state(&source.inner)
            }
            fn read_state_cuboid(&self, source: &crate::magnets::CuboidMagnet) -> bool {
                self.inner.read_state(&source.inner)
            }
            fn read_state_dipole(&self, source: &crate::magnets::Dipole) -> bool {
                self.inner.read_state(&source.inner)
            }
            fn read_state_collection(&self, source: &crate::collection::SourceCollection) -> bool {
                self.inner.read_state(&source.inner)
            }

            fn read(&self, source: pyo3::Bound<'_, pyo3::PyAny>) -> pyo3::PyResult<bool> {
                if let Ok(m) = source.extract::<pyo3::PyRef<'_, crate::magnets::CylinderMagnet>>() {
                    Ok(self.read_state_cylinder(&m))
                } else if let Ok(m) =
                    source.extract::<pyo3::PyRef<'_, crate::magnets::CuboidMagnet>>()
                {
                    Ok(self.read_state_cuboid(&m))
                } else if let Ok(m) = source.extract::<pyo3::PyRef<'_, crate::magnets::Dipole>>() {
                    Ok(self.read_state_dipole(&m))
                } else if let Ok(m) =
                    source.extract::<pyo3::PyRef<'_, crate::collection::SourceCollection>>()
                {
                    Ok(self.read_state_collection(&m))
                } else {
                    Err(pyo3::exceptions::PyTypeError::new_err(
                        "source must be CylinderMagnet, CuboidMagnet, Dipole, or SourceCollection",
                    ))
                }
            }
        }
    };
}
