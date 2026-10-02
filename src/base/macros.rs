/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

macro_rules! try_into_slice {
    ($obj:ident) => {
        $obj.map(|inner| inner.0).unwrap_or([0.0; _])
    };
}
pub(crate) use try_into_slice;

macro_rules! try_into_slice_or {
    ($obj:ident, $default:expr) => {
        $obj.map(|inner| inner.0).unwrap_or($default)
    };
}
pub(crate) use try_into_slice_or;

macro_rules! try_into_quat {
    ($obj:ident) => {
        $obj.map(|inner| inner.0)
            .unwrap_or(nalgebra::UnitQuaternion::identity())
    };
}
pub(crate) use try_into_quat;

macro_rules! get_state_item {
    ($state:expr, $key:literal) => {
        $state.get_item($key)?.ok_or_else(|| {
            pyo3::exceptions::PyKeyError::new_err(concat!(
                "Missing required state key: '",
                $key,
                "'"
            ))
        })
    };
    ($state:expr, $key:ident) => {
        $state.get_item(stringify!($key))?.ok_or_else(|| {
            pyo3::exceptions::PyKeyError::new_err(concat!(
                "Missing required state key: '",
                stringify!($key),
                "'"
            ))
        })
    };
    ($state:expr, $key:literal, $type:ty) => {
        $crate::base::get_state_item!($state, $key)?.extract::<$type>()
    };
    ($state:expr, $key:ident, $type:ty) => {
        $crate::base::get_state_item!($state, $key)?.extract::<$type>()
    };
}
pub(crate) use get_state_item;

macro_rules! extract_states {
    (@extract $state:expr, $arg:tt) => {
        let $arg: f64 = $crate::base::get_state_item!($state, $arg, f64)?;
    };
    (@extract $state:expr, $arg:tt, $size:expr) => {
        let $arg: [f64; $size] = $crate::base::get_state_item!($state, $arg, [f64; $size])?;
    };
    ($state:expr, [$($arg:tt $(; $size:expr)?),*]) => {
        $(
            extract_states!(@extract $state, $arg $(, $size)?);
        )*
    };
}
pub(crate) use extract_states;

macro_rules! try_extract {
    ($obj:expr, $( $variant:ident => $type:ty ),* $(,)?) => {
        $(
            if $obj.is_exact_instance_of::<$type>() {
                if let Ok(m) = $obj.extract::<pyo3::PyRef<'_, $type>>() {
                    return Ok(Self::$variant(m));
                }
            }
        )*
        $(
            if let Ok(m) = $obj.extract::<pyo3::PyRef<'_, $type>>() {
                return Ok(Self::$variant(m));
            }
        )*
    };
}
pub(crate) use try_extract;
