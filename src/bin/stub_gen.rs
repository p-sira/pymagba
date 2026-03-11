/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

#[cfg(feature = "stub-gen")]
fn main() -> pyo3_stub_gen::Result<()> {
    use pymagba_binding::stub_info;
    let stub_info = stub_info()?;
    stub_info.generate()?;

    Ok(())
}

#[cfg(not(feature = "stub-gen"))]
fn main() {}
