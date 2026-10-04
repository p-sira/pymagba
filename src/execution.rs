/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

//! Calibration-only interpreter execution controls.

use core::sync::atomic::{AtomicBool, AtomicU64, AtomicU8, Ordering};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[repr(u8)]
pub(crate) enum GilMode {
    Auto = 0,
    Retain = 1,
    Detach = 2,
}

static MODE: AtomicU8 = AtomicU8::new(GilMode::Auto as u8);
static INSTRUMENT: AtomicBool = AtomicBool::new(false);
static RETAINED_BRANCHES: AtomicU64 = AtomicU64::new(0);
static DETACHED_BRANCHES: AtomicU64 = AtomicU64::new(0);

pub(crate) fn set_gil_mode(mode: GilMode) {
    MODE.store(mode as u8, Ordering::Relaxed);
}

pub(crate) fn gil_mode() -> GilMode {
    match MODE.load(Ordering::Relaxed) {
        1 => GilMode::Retain,
        2 => GilMode::Detach,
        _ => GilMode::Auto,
    }
}

pub(crate) fn set_instrumentation(enabled: bool) {
    INSTRUMENT.store(enabled, Ordering::Relaxed);
}

pub(crate) fn instrumentation() -> bool {
    INSTRUMENT.load(Ordering::Relaxed)
}

pub(crate) fn reset_branch_counts() {
    RETAINED_BRANCHES.store(0, Ordering::Relaxed);
    DETACHED_BRANCHES.store(0, Ordering::Relaxed);
}

pub(crate) fn branch_counts() -> (u64, u64) {
    (
        RETAINED_BRANCHES.load(Ordering::Relaxed),
        DETACHED_BRANCHES.load(Ordering::Relaxed),
    )
}

#[inline]
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

#[cfg(test)]
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
