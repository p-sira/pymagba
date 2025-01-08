/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use pyo3::prelude::*;
mod field;
mod special;

macro_rules! add_submodule {
    ($rust_module: ident, $name: expr, $py: expr, $m: expr) => {
        let submodule = PyModule::new($py, &format!("{}", $name))?;
        $rust_module::register_functions(&submodule)?;
        $m.add_submodule(&submodule)?;
    };
}

#[pymodule]
fn pymagba_binding(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    add_submodule!(special, "special", py, m);
    add_submodule!(field, "fields", py, m);
    Ok(())
}
