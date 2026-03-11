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
                let source_ref = crate::base::SourceRef::try_extract(&source)?;
                let output = self.inner.read(source_ref.as_source());
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
