/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

//! Interpreter detachment thresholds and calibration-only overrides.

#[cfg(feature = "threshold-calibration")]
use core::sync::atomic::{AtomicBool, AtomicU64, AtomicU8, Ordering};

// Calibrated on a 12-logical-CPU x86-64 host. These intentionally match the
// conservative Rayon cutovers so small serial calls avoid GIL transition cost.
pub(crate) const CIRCULAR_THRESHOLD: usize = 1023;
pub(crate) const CUBOID_THRESHOLD: usize = 159;
pub(crate) const CYLINDER_THRESHOLD: usize = 767;
pub(crate) const DIPOLE_THRESHOLD: usize = 24575;
pub(crate) const MESH_THRESHOLD: usize = 15;
pub(crate) const PATH_THRESHOLD: usize = 409;
pub(crate) const SHEET_THRESHOLD: usize = 47;
pub(crate) const SPHERE_THRESHOLD: usize = 24575;
pub(crate) const TETRAHEDRON_THRESHOLD: usize = 159;
pub(crate) const TRIANGLE_THRESHOLD: usize = 818;
pub(crate) const TRIANGLE_CURRENT_THRESHOLD: usize = 255;

#[cfg(feature = "threshold-calibration")]
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[repr(u8)]
pub(crate) enum GilMode {
    Auto = 0,
    Retain = 1,
    Detach = 2,
}

#[cfg(feature = "threshold-calibration")]
static MODE: AtomicU8 = AtomicU8::new(GilMode::Auto as u8);
#[cfg(feature = "threshold-calibration")]
static INSTRUMENT: AtomicBool = AtomicBool::new(false);
#[cfg(feature = "threshold-calibration")]
static RETAINED_BRANCHES: AtomicU64 = AtomicU64::new(0);
#[cfg(feature = "threshold-calibration")]
static DETACHED_BRANCHES: AtomicU64 = AtomicU64::new(0);

#[cfg(feature = "threshold-calibration")]
pub(crate) fn set_gil_mode(mode: GilMode) {
    MODE.store(mode as u8, Ordering::Relaxed);
}

#[cfg(feature = "threshold-calibration")]
pub(crate) fn gil_mode() -> GilMode {
    match MODE.load(Ordering::Relaxed) {
        1 => GilMode::Retain,
        2 => GilMode::Detach,
        _ => GilMode::Auto,
    }
}

#[cfg(feature = "threshold-calibration")]
pub(crate) fn set_instrumentation(enabled: bool) {
    INSTRUMENT.store(enabled, Ordering::Relaxed);
}

#[cfg(feature = "threshold-calibration")]
pub(crate) fn instrumentation() -> bool {
    INSTRUMENT.load(Ordering::Relaxed)
}

#[cfg(feature = "threshold-calibration")]
pub(crate) fn reset_branch_counts() {
    RETAINED_BRANCHES.store(0, Ordering::Relaxed);
    DETACHED_BRANCHES.store(0, Ordering::Relaxed);
}

#[cfg(feature = "threshold-calibration")]
pub(crate) fn branch_counts() -> (u64, u64) {
    (
        RETAINED_BRANCHES.load(Ordering::Relaxed),
        DETACHED_BRANCHES.load(Ordering::Relaxed),
    )
}

#[inline]
#[cfg(feature = "threshold-calibration")]
pub(crate) fn should_detach(auto: bool) -> bool {
    let detach = match gil_mode() {
        GilMode::Auto => auto,
        GilMode::Retain => false,
        GilMode::Detach => true,
    };

    if instrumentation() {
        if detach {
            DETACHED_BRANCHES.fetch_add(1, Ordering::Relaxed);
        } else {
            RETAINED_BRANCHES.fetch_add(1, Ordering::Relaxed);
        }
    }
    detach
}

#[inline]
#[cfg(not(feature = "threshold-calibration"))]
pub(crate) const fn should_detach(auto: bool) -> bool {
    auto
}

#[cfg(all(test, feature = "threshold-calibration"))]
mod tests {
    use super::*;

    #[test]
    fn modes_override_automatic_choice() {
        set_instrumentation(true);
        reset_branch_counts();

        set_gil_mode(GilMode::Retain);
        assert!(!should_detach(true));
        set_gil_mode(GilMode::Detach);
        assert!(should_detach(false));
        set_gil_mode(GilMode::Auto);
        assert!(should_detach(true));
        assert!(!should_detach(false));

        assert_eq!(branch_counts(), (2, 2));
        set_instrumentation(false);
    }
}
