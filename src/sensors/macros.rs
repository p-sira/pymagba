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
        }
    };
}
