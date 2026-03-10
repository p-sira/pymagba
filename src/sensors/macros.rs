/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

macro_rules! impl_unified_read {
    ($struct:ty, $output_type:ty, $variant:ident) => {
        #[pyo3::pymethods]
        impl $struct {
            fn read(&self, source: pyo3::Bound<'_, pyo3::PyAny>) -> pyo3::PyResult<$output_type> {
                use magba::base::Observer;
                let output = if let Ok(m) =
                    source.extract::<pyo3::PyRef<'_, crate::magnets::CylinderMagnet>>()
                {
                    self.inner.read(&m.inner)
                } else if let Ok(m) =
                    source.extract::<pyo3::PyRef<'_, crate::magnets::CuboidMagnet>>()
                {
                    self.inner.read(&m.inner)
                } else if let Ok(m) = source.extract::<pyo3::PyRef<'_, crate::magnets::Dipole>>() {
                    self.inner.read(&m.inner)
                } else if let Ok(m) =
                    source.extract::<pyo3::PyRef<'_, crate::magnets::SphereMagnet>>()
                {
                    self.inner.read(&m.inner)
                } else if let Ok(m) =
                    source.extract::<pyo3::PyRef<'_, crate::currents::CircularCurrent>>()
                {
                    self.inner.read(&m.inner)
                } else if let Ok(m) =
                    source.extract::<pyo3::PyRef<'_, crate::collection::SourceCollection>>()
                {
                    self.inner.read(&m.inner)
                } else {
                    return Err(pyo3::exceptions::PyTypeError::new_err(
                        "source must be a valid Magnet, Current, or SourceCollection",
                    ));
                };

                impl_unified_read!(@convert output, $variant)
            }
        }
    };

    (@convert $output:expr, Scalar) => {
        if let magba::base::SensorOutput::Scalar(val) = $output {
            Ok(val)
        } else {
            Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Expected Scalar output",
            ))
        }
    };

    (@convert $output:expr, Digital) => {
        if let magba::base::SensorOutput::Digital(val) = $output {
            Ok(val != 0)
        } else {
            Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Expected Digital output",
            ))
        }
    };
}
