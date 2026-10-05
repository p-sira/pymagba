/*
 * Magba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

#[cfg(feature = "stub-gen")]
fn main() -> pyo3_stub_gen::Result<()> {
    use pymagba_binding::stub_info;
    let stub_info = stub_info()?;
    stub_info.generate()?;

    // Post-processing to fix type inference for subclasses
    // Replace "-> ClassName:" with "-> typing.Self:" for all __new__ methods.
    use regex::Regex;
    use std::fs;

    let path = "python/pymagba/pymagba_binding/__init__.pyi";
    let content = fs::read_to_string(path)?;

    let re = Regex::new(r"(?m)^( +def __new__\(.*?\) -> )[a-zA-Z0-9_.]+(.*)$")
        .expect("Failed to compile regex");

    let new_content = re.replace_all(&content, "${1}typing.Self${2}");

    fs::write(path, new_content.as_ref()).expect("Failed to write stub file");

    // Format generated stub file with ruff if available
    let _ = std::process::Command::new("uv")
        .args(["run", "ruff", "check", "--fix", path])
        .status()
        .or_else(|_| {
            std::process::Command::new("ruff")
                .args(["check", "--fix", path])
                .status()
        });

    let _ = std::process::Command::new("uv")
        .args(["run", "ruff", "format", path])
        .status()
        .or_else(|_| {
            std::process::Command::new("ruff")
                .args(["format", path])
                .status()
        });

    Ok(())
}

#[cfg(not(feature = "stub-gen"))]
fn main() {}
