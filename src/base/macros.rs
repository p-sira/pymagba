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
        $obj.map(|inner| inner.0).unwrap_or(nalgebra::UnitQuaternion::identity())
    };
}
pub(crate) use try_into_quat;
