/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use pymagba_binding::stub_info;
use pyo3_stub_gen::Result;

fn main() -> Result<()> {
    let stub_info = stub_info()?;
    stub_info.generate()?;

    Ok(())
}
