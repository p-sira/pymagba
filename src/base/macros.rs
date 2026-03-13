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

macro_rules! extract_states {
    (@extract $state:expr, $arg:tt) => {
        let $arg: f64 = $state.get_item(stringify!($arg))?.unwrap().extract()?;
    };
    (@extract $state:expr, $arg:tt, $size:expr) => {
        let $arg: [f64; $size] = $state.get_item(stringify!($arg))?.unwrap().extract()?;
    };
    ($state:expr, [$($arg:tt $(; $size:expr)?),*]) => {
        $(
            extract_states!(@extract $state, $arg $(, $size)?);
        )*
    };
}
pub(crate) use extract_states;
