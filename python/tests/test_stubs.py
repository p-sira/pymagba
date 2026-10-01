"""Tests verifying that python type stubs are up to date and complete."""

import ast
import inspect
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pymagba.pymagba_binding as binding
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STUB_PATH = REPO_ROOT / "python" / "pymagba" / "pymagba_binding" / "__init__.pyi"

IGNORED_DUNDERS = {
    "__class__",
    "__delattr__",
    "__dir__",
    "__doc__",
    "__eq__",
    "__format__",
    "__ge__",
    "__getattribute__",
    "__gt__",
    "__hash__",
    "__init_subclass__",
    "__le__",
    "__lt__",
    "__module__",
    "__ne__",
    "__new__",
    "__reduce__",
    "__reduce_ex__",
    "__repr__",
    "__setattr__",
    "__sizeof__",
    "__str__",
    "__subclasshook__",
    "__copy__",
    "__deepcopy__",
}

CRITICAL_DUNDERS = {"__len__", "__getitem__", "__getstate__", "__setstate__"}


def parse_stub_ast(stub_file: Path) -> tuple[dict[str, set[str]], set[str], list[str]]:
    """Parse the stub file and extract classes, functions, and __all__."""
    assert stub_file.exists(), f"Stub file not found at {stub_file}"
    content = stub_file.read_text(encoding="utf-8")
    tree = ast.parse(content)

    classes: dict[str, set[str]] = {}
    functions: set[str] = set()
    all_exports: list[str] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = {
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            classes[node.name] = methods
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "__all__"
                    and isinstance(node.value, (ast.List, ast.Tuple))
                ):
                    all_exports = [
                        elt.value
                        for elt in node.value.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    ]

    return classes, functions, all_exports


def test_stub_file_exists():
    """Verify that the stub file exists and is not empty."""
    assert STUB_PATH.is_file(), f"Missing stub file: {STUB_PATH}"
    assert STUB_PATH.stat().st_size > 0, "Stub file is empty"


def test_stub_covers_all_runtime_symbols():
    """Ensure that all runtime classes, methods, and functions are declared in stubs.

    If this test fails, you likely forgot to run 'cargo stub-gen' after modifying
    Rust PyO3 bindings.
    """
    classes, functions, all_exports = parse_stub_ast(STUB_PATH)
    missing: list[str] = []

    for name, obj in inspect.getmembers(binding):
        if inspect.isclass(obj):
            if name not in classes:
                missing.append(f"Class '{name}' missing from stubs")
                continue
            if name not in all_exports:
                missing.append(f"Class '{name}' missing from stub __all__")

            stub_methods = classes[name]
            for attr_name in dir(obj):
                if attr_name in IGNORED_DUNDERS:
                    continue
                if attr_name.startswith("__") and attr_name.endswith("__"):
                    if attr_name in CRITICAL_DUNDERS and attr_name not in stub_methods:
                        missing.append(
                            f"Method '{name}.{attr_name}' missing from stubs"
                        )
                    continue
                if attr_name not in stub_methods:
                    missing.append(f"Member '{name}.{attr_name}' missing from stubs")

        elif inspect.isbuiltin(obj) or inspect.isfunction(obj):
            if name not in functions:
                missing.append(f"Function '{name}' missing from stubs")
            if name not in all_exports:
                missing.append(f"Function '{name}' missing from stub __all__")

    assert not missing, (
        f"Stubs in {STUB_PATH} are out of date with runtime PyO3 bindings!\n"
        + "\n".join(f"  - {m}" for m in missing)
        + "\n\nFix: Run 'cargo stub-gen' (or 'cargo run --bin stub_gen --no-default-features --features stub-gen') and commit the updated stub file."
    )


@pytest.mark.skipif(
    shutil.which("cargo") is None, reason="cargo is not available in environment"
)
@pytest.mark.skipif(
    "CI" in os.environ,
    reason="CI verifies stub freshness in a dedicated workflow step",
)
def test_stub_freshness_with_cargo_stub_gen():
    """Verify that running 'cargo stub-gen' produces identical content to committed stubs."""
    original_content = STUB_PATH.read_text(encoding="utf-8")

    env = os.environ.copy()
    env["PYO3_PYTHON"] = sys.executable
    lib_dir = str(Path(sys.executable).parent.parent / "lib")
    env["LD_LIBRARY_PATH"] = f"{lib_dir}:{env.get('LD_LIBRARY_PATH', '')}"

    result = subprocess.run(
        [
            "cargo",
            "run",
            "--bin",
            "stub_gen",
            "--no-default-features",
            "--features",
            "stub-gen",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"cargo stub-gen failed:\n{result.stderr}"

    new_content = STUB_PATH.read_text(encoding="utf-8")
    assert new_content == original_content, (
        f"Generated stubs differ from committed file {STUB_PATH}!\n"
        "Please run 'cargo stub-gen' and commit the updated file."
    )


def test_consumer_mypy_typing():
    """Verify that consumer Python code using sensors and magnets typechecks with mypy."""
    mypy_api = pytest.importorskip("mypy.api")

    code = """
from pymagba.magnets import CylinderMagnet, CuboidMagnet, SphereMagnet
from pymagba.sensors import HallLatch, HallSwitch, LinearHallSensor

m = CylinderMagnet()
latch: bool = HallLatch().read(m)
switch: bool = HallSwitch().read(m)
reading: float = LinearHallSensor().read(m)
"""
    stdout, stderr, exit_status = mypy_api.run(["-c", code])
    assert exit_status == 0, (
        f"Consumer mypy type checking failed!\nstdout:\n{stdout}\nstderr:\n{stderr}"
    )
