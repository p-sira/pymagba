/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

macro_rules! impl_read_voltage {
    ($Struct:ty) => {
        #[pyo3::pymethods]
        impl $Struct {
            /// Compute the analog output voltage (V) in the presence of a ``CylinderMagnet`` source.
            ///
            /// Returns:
            ///     float: Output voltage in volts, clamped to ``[0, supply_voltage]``.
            fn read_voltage_cylinder(&self, source: &crate::magnets::CylinderMagnet) -> f64 {
                self.inner.read_voltage(&source.inner)
            }
            /// Compute the analog output voltage (V) in the presence of a ``CuboidMagnet`` source.
            ///
            /// Returns:
            ///     float: Output voltage in volts, clamped to ``[0, supply_voltage]``.
            fn read_voltage_cuboid(&self, source: &crate::magnets::CuboidMagnet) -> f64 {
                self.inner.read_voltage(&source.inner)
            }
            /// Compute the analog output voltage (V) in the presence of a ``Dipole`` source.
            ///
            /// Returns:
            ///     float: Output voltage in volts, clamped to ``[0, supply_voltage]``.
            fn read_voltage_dipole(&self, source: &crate::magnets::Dipole) -> f64 {
                self.inner.read_voltage(&source.inner)
            }
            /// Compute the analog output voltage (V) in the presence of a ``SourceCollection``.
            ///
            /// Returns:
            ///     float: Output voltage in volts, clamped to ``[0, supply_voltage]``.
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
            /// Read the digital state of the sensor in the presence of a ``CylinderMagnet`` source.
            ///
            /// Returns:
            ///     bool: ``True`` if ON, ``False`` otherwise.
            fn read_state_cylinder(&self, source: &crate::magnets::CylinderMagnet) -> bool {
                self.inner.read_state(&source.inner)
            }
            /// Read the digital state of the sensor in the presence of a ``CuboidMagnet`` source.
            ///
            /// Returns:
            ///     bool: ``True`` if ON, ``False`` otherwise.
            fn read_state_cuboid(&self, source: &crate::magnets::CuboidMagnet) -> bool {
                self.inner.read_state(&source.inner)
            }
            /// Read the digital state of the sensor in the presence of a ``Dipole`` source.
            ///
            /// Returns:
            ///     bool: ``True`` if ON, ``False`` otherwise.
            fn read_state_dipole(&self, source: &crate::magnets::Dipole) -> bool {
                self.inner.read_state(&source.inner)
            }
            /// Read the digital state of the sensor in the presence of a ``SourceCollection``.
            ///
            /// Returns:
            ///     bool: ``True`` if ON, ``False`` otherwise.
            fn read_state_collection(&self, source: &crate::collection::SourceCollection) -> bool {
                self.inner.read_state(&source.inner)
            }
        }
    };
}
