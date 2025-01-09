/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

#[macro_export]
macro_rules! add_submodule {
    ($rust_module: ident, $name: expr, $py: expr, $m: expr) => {
        let submodule = PyModule::new($py, &format!("{}", $name))?;
        $rust_module::register_functions(&submodule)?;
        $m.add_submodule(&submodule)?;
    };
}

#[macro_export]
macro_rules! fn_err {
    ($func_name: expr, $e: expr) => {
        Err(PyRuntimeError::new_err(format!(
            "PyFn {}: Fail due to rust {}",
            $func_name, $e,
        )))
    };
}
