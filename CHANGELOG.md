# CHANGELOG

## 0.7.0

This version corresponds to Magba v0.7.3.

### Bug Fixes

#### Validation & Error Handling

- Fix mesh error message formatting using `Display` and stabilize validation tests for Magba v0.7.0. [#39](https://github.com/p-sira/pymagba/pull/39)
- Validate numerical inputs (finite and non-zero quaternions with scaled normalization, valid sensitive axes for sensors, and valid geometry dimensions for free field functions) and ensure setters preserve previous state on invalid input. [#42](https://github.com/p-sira/pymagba/pull/42)
- Handle missing dictionary keys in `__setstate__` with `KeyError` via `get_state_item!`, propagate child validation errors during collection deserialization, and ensure state restoration failures preserve original state without leaking panics. [#43](https://github.com/p-sira/pymagba/pull/43)
- Require `SheetCurrent` and `sheet_current_B` current densities to match mesh face count (with explicit zero-density default when omitted), preventing silent data truncation. [#43](https://github.com/p-sira/pymagba/pull/43)

#### Collections & Serialization

- Fix `SourceCollection` and `ObserverCollection` pickle deserialization double-offsetting initial poses. [#40](https://github.com/p-sira/pymagba/pull/40)
- Fix dynamic mutation of collection children (`collection[i]`) not propagating to parent magnetic field evaluations or sensor readings. [#40](https://github.com/p-sira/pymagba/pull/40)
- Preserve `HallLatch` hysteresis state during pickle serialization and deserialization. [#40](https://github.com/p-sira/pymagba/pull/40)

#### Memory Management

- Reject collection containment cycles (preventing infinite recursion and stack overflows in `SourceCollection` during initialization, append, and deserialization). [#45](https://github.com/p-sira/pymagba/pull/45)
- Integrate Python cyclic garbage collection (`__traverse__` and `__clear__`) for `SourceCollection` and `ObserverCollection` to collect reference cycles involving Python subclass attributes or child object backreferences. [#45](https://github.com/p-sira/pymagba/pull/45)

#### Typing & Documentation

- Fix sensor `read()` method missing from Python type stubs (`HallLatch`, `HallSwitch`, `LinearHallSensor`). [#44](https://github.com/p-sira/pymagba/pull/44)
- Correct default polarization vector documentation in `CylinderMagnet`, `CuboidMagnet`, `SphereMagnet`, and corresponding free field functions (`cylinder_B`, `cuboid_B`, `sphere_B`) from `[0.0, 0.0, 0.0]` to `[0.0, 0.0, 1.0]`. [#45](https://github.com/p-sira/pymagba/pull/45)

### Performance Improvements

#### Execution & Concurrency

- Add release compiler profile in `Cargo.toml` (`opt-level = 3`, `lto = "fat"`, `codegen-units = 1`, `strip = true`), reducing compiled library binary size by 40% (2.12 MB → 1.28 MB) and maximizing cross-crate inlining across `magba`, `openmesh`, `ellip`, and `nalgebra`. [#46](https://github.com/p-sira/pymagba/pull/46)
- Eliminate Python GIL thread contention: detach GIL during compute-intensive batch evaluations across magnet and current classes and `SourceCollection`, enabling concurrent Python worker thread progress. [#46](https://github.com/p-sira/pymagba/pull/46)
- Implement scalar fast-path: bypass GIL detachment overhead when evaluating single observation points ($N \le 1$) across all 11 free field functions, magnet classes, and collections. [#46](https://github.com/p-sira/pymagba/pull/46)
- Tune GIL release thresholds by computational complexity: defer GIL detachment up to $N \le 32$ for lightweight sources (`Dipole`, `SphereMagnet`, `dipole_B`, `sphere_B`), reducing micro-batch evaluation latency by 20%–30% without impacting multithreaded responsiveness. [#49](https://github.com/p-sira/pymagba/pull/49)
- Tune FFI parallelization thresholds with full Python-to-Rust call path wall-time measurements. [#55](https://github.com/p-sira/pymagba/pull/55)

#### Data Conversion

- Implement zero-copy buffer conversion in `vec3_to_pyarray2`: construct single-point 2D arrays directly, and convert contiguous `Vec<Vector3<f64>>` to `PyArray2` without redundant intermediate heap buffer re-allocations (saving 24 MB per 1M points). [#46](https://github.com/p-sira/pymagba/pull/46)
- Implement bulk `float32` extraction in `PointsLike` and `ArrayLike3`: vectorize contiguous 2D float32 slice conversion using `as_chunks::<3>()`, eliminating the 17x element-by-element Python iteration penalty. [#46](https://github.com/p-sira/pymagba/pull/46)
- Optimize rotation extraction in `PyRotation`: prioritize direct 1D NumPy array and sequence extraction, eliminate `AttributeError` exceptions on array inputs, and extract SciPy quaternion buffers directly, achieving up to 4.3x speedup on rotate operations. [#47](https://github.com/p-sira/pymagba/pull/47)
- Implement zero-copy buffer borrowing and stack allocation in `PointsLike`: borrow C-contiguous `(N, 3)` `float64` NumPy arrays directly as `&[Point3<f64>]` without copying or heap allocation, and store single points on the stack via `PointsStorage::Single([Point3<f64>; 1])`, completely eliminating heap allocation and copy overhead on batch evaluation. [#51](https://github.com/p-sira/pymagba/pull/51)

#### Caching & Dispatch

- Transparently cache verified `TriMesh` geometry in `mesh_B` and `sheet_current_B`: maintain a budgeted LRU cache (capped at 8 entries and 200k faces) of compiled topological mesh structures across repeated functional calls with identical vertex and face buffers, accelerating realistic mesh evaluations by up to 11.2x on single meshes and up to 9.0x in multi-mesh loops without thrashing or memory leaks. [#50](https://github.com/p-sira/pymagba/pull/50)
- Accelerate source and observer reference extraction with exact type pointer dispatch in `SourceRef` and `ObserverRef`, bypassing sequential Python MRO subclass traversal for concrete instances. [#48](https://github.com/p-sira/pymagba/pull/48)
- Cache `SourceAssembly` in `SourceCollection`: cache compiled `SourceAssembly` across repeated `compute_B` evaluations and observer `read_all` calls using lightweight child state fingerprints (hashing pose and intrinsic physical parameters per source), updating assembly poses in-place via `Transform::set_pose` when the collection transforms, and bypassing expensive component re-cloning and assembly rebuilding when child sources are unchanged. [#52](https://github.com/p-sira/pymagba/pull/52)

### Tooling & Typing

- Add automated Python type stub generation and enforcement system. [#44](https://github.com/p-sira/pymagba/pull/44)
  - Add `cargo stub-gen` alias in `.cargo/config.toml` for convenient one-step stub generation.
  - Automate ruff formatting and lint fixes on generated stubs in `src/bin/stub_gen.rs`.
  - Add pre-commit hook in `.githooks/pre-commit` and setup script `scripts/setup_git_hooks.sh` to block commits with outdated stubs when Rust sources are modified.
  - Add test suite in `python/tests/test_stubs.py` verifying stub symbol completeness against runtime PyO3 bindings, generator freshness, and consumer typing with `mypy`.
  - Add CI workflow verification in GitHub Actions to ensure stubs remain synchronized and type-checked on all pull requests.
  - Optimize release workflow (`publish.yml`) to only trigger on release tags and manual dispatch, avoiding redundant 16-wheel cross-compilations on pull requests.

### Dependencies

- Remove `magpylib` from runtime dependencies list (retaining it in the dev dependency group for comparison benchmarks).

## 0.6.0

This version corresponds to Magba v0.6.2.

### New Features

- Implement pure functions `path_current_B`, `sheet_current_B`, and `triangle_current_B`.

## Benchmarks

- Add performance comparison against MagpyLib.

## 0.5.1

### Documentation

- Add `Currents`, `TriangleMagnet`, `TetrahedronMagnet`, `MeshMagnet`, and `ObserverCollection` documentation.

## 0.5.0

This version corresponds to Magba v0.6.2.

### New Features

- Add new magnets: `TriangleMagnet`, `TetrahedronMagnet`, and `MeshMagnet`.
- Add new current geometries: `PathCurrent`, `TriangleCurrent`, and `SheetCurrent`.
- Support loading stl files via `from_stl()` class method for `SheetCurrent` and `MeshMagnet`.

### Testing

- Delegate the test generation to external `p-sira/magba-testing` repository, which is included as a git submodule at `testing/`.
- Standardize the tests between Magba and PyMagba.

## 0.4.1

This version corresponds to Magba v0.4.3.

### New Features

- Add `read_state` for `HallLatch` and `HallSwitch`.

### Bug Fixes

- Fix collection constructors interpreting children pose as in local frame. Now assume children poses in global frame.
- Fix stub return types from `pymagba_binding` classes to `pymagba` classes.
- Use `ArrayLike` in stubs instead of Sequence.
- Fix default polarization vectors of magnet classes to [0, 0, 1].

## 0.4.0

This version corresponds to Magba v0.4.2.

### New Features

- **Index, Append, Len:** Implement for `SourceCollection` and `ObserverCollection`.
- **Pickle Support:** Allow PyMagba objects to be packed into Python dict, pickled, and reconstruct from the dict.
- **Field Functions:** Direct access to magnetic field functions, which support parallelization.
- **Stubs:** Add stubs for autocomplete and typehinting.
- **Benchmarks:** Publish benchmark results generated by ASV.

### Improvements

- **Improve Performance:** Reduce Python object parsing overhead.
- **Improve Documentation:** Add common sections for transformation and source methods for easy comprehension.

### Internal Structure Improvements

- Implement `SourceRef` and `ObserverRef` enums to facilitate polymorphic Python class extraction.

## 0.3.0

- Use PyO3's PyClass to bind directly to Magba structs.

## 0.1.0

- Initial release
