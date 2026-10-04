# Python FFI threshold calibration plan

## Objective and scope

Calibrate PyMagba's execution policy using complete Python call timings, including
argument conversion, result allocation, Rust computation, and NumPy wrapping.
Apply the useful methodology from [EllipPy PR #31](https://github.com/p-sira/ellippy/pull/31)
with explicit, independently verified serial and parallel modes.

Magba dependency version changes are handled by the separate PR. This plan covers
the calibration contract with Magba, Python benchmarks, PyMagba's detach policy,
sensor reads, and validation. Keep the public Python API unchanged.

## Current behavior

- `src/fields.rs::detach_if_multi!` and `src/macros.rs::impl_compute_B!`
  retain the GIL through one point by default; Dipole and Sphere use 32 points.
- `src/collection.rs::SourceCollection.compute_B` detaches above one point.
- Individual sensor `read()`, `read_voltage()`, `read_state()`, and
  `compute_B_perp()` methods evaluate one source point while holding the GIL.
  Their cost is driven by source complexity rather than a point count.
- `ObserverCollection.read_all()` evaluates sensors sequentially and creates
  Python list items inside the loop, so it holds the GIL for the entire operation.
- Magba independently selects serial or Rayon execution inside its batch kernels.
  Changing a PyMagba detach threshold does not change that selection.
- `src/util.rs::vec3_to_pyarray2` transfers the existing result buffer for batches
  larger than one; calibration must preserve this path and its singleton case.
- `benchmarks/benchmarks_ffi.py::SmallBatchScaling` covers several source classes,
  but needs functional calls, more geometries, and sizes around actual cutovers.

## 1. Establish trustworthy calibration controls

Add a non-default `threshold-calibration` Cargo feature and private calibration
controls. Normal builds must contain no environment lookups, mutable calibration
policy, or extra Python exports on the hot path.

Provide independent controls:

| Control | Modes | Owner |
| --- | --- | --- |
| Rust execution | `auto`, `serial`, `parallel` | Magba |
| Interpreter detachment | `auto`, `retain`, `detach` | PyMagba |

Coordinate a calibration-only Magba interface that forces the actual batch
kernels in both functional and object calls. Collection overrides must propagate
to all relevant dispatch sites, including sum and assembly paths. If the separate
Magba PR does not supply this interface, add it as a prerequisite change there;
do not emulate serial execution with repeated Python scalar calls.

Forced `serial` must bypass Rayon at every input size. Forced `parallel` must
bypass the usual size threshold. One Rayon worker is not a serial baseline.
Use calibration-only branch counters or equivalent instrumentation to verify
which path ran; disable instrumentation during measurements.

Run configurations in isolated worker processes, configured before timing and
before Rayon pool initialization. Avoid changing process-global controls while
calls are active. Record the loaded extension path and effective controls so a
stale or ordinary build cannot silently produce calibration results.

## 2. Build the Python calibration harness

Add `benchmarks/calibrate_thresholds.py`, executable directly from the repository.
Reuse representative geometry definitions from existing benchmarks where practical
without introducing a dependency on running pytest or ASV.

The harness should:

- Build inputs outside the timed region and use identical seeded inputs for each
  policy comparison. Use valid, nonzero physical parameters and avoid accidental
  singularities in performance fixtures.
- Measure complete public Python calls on release builds. Verify equivalent
  numerical results before timing each case.
- Warm each worker and Rayon pool. Time blocks of repeated calls, collect repeated
  samples, and alternate configuration order to reduce drift. Keep output disposal
  consistent across modes.
- Start with a logarithmic size sweep, then refine around candidate transitions.
  Include 0, 1, 2, 4, 8, 16, 32, 64 and sizes around existing cutovers; extend large
  batches until a stable advantage or the configured resource limit is reached.
- Require a repeatable advantage, initially at least 5%, across neighboring sizes
  and independent repeats. Do not assume noisy timings are monotonic or use a
  binary search as the sole evidence.
- Report `no_crossover` or `inconclusive` explicitly. Never substitute the maximum
  tested size as if it were a measured crossover.
- Save raw timing samples, summaries, candidate policies, and provenance as JSON
  under a configurable results directory. Include CPU, OS, Python/NumPy versions,
  GIL mode, Rust compiler, repository revisions, build options, and Rayon threads.

Cover all eleven field/source geometries through both functional and object APIs.
Use contiguous `float64` arrays for primary calibration; validate candidates with
strided arrays, `float32` inputs, Python lists, and singleton representations.
Include axial and mixed cylinder polarization and varied point distributions.

For Mesh, Path, and Sheet, vary face or segment counts. For collections, vary
source count, homogeneous versus mixed sources, and nesting. Separate steady-state
geometry/assembly reuse from first-call or invalidated-cache costs.

Cover sensor entry points as a separate benchmark family. Test each sensor type's
unified `read()` and specialized method against cheap sources, variable-complexity
sources, and `SourceCollection`. For `ObserverCollection.read_all()`, vary sensor
count, sensor mix, source type and complexity, repeated child references, and latch
state transitions. Compare empty, singleton, small, transition, and large observer
collections. The existing `python/benchmarks/test_bench_sensors.py` cases form the
baseline but need cutover-adjacent sizes and source-complexity parameters.

## 3. Select Rayon and detach policies separately

First compare forced serial and parallel execution with both paths detached. This
isolates the Rayon choice while retaining realistic Python allocation and wrapping
costs. Shared FFI overhead can dilute percentage speedups; it does not by itself
move the exact equality point between the two paths.

Next, with the proposed Rust dispatch policy fixed, compare retaining versus
detaching the interpreter. Detachment is also a responsiveness decision: retaining
the GIL may remain faster in isolated latency measurements even for long calls.
Select a conservative small-work cutoff using latency evidence and a concurrent
Python-thread responsiveness check. Do not retain the GIL throughout large Rayon
computations merely because doing so saves a detach round trip.

Finally, validate the combined automatic policy against the current implementation
and the forced baselines. Test multiple Rayon thread counts and, when available,
a second CPU architecture. Record hardware limitations rather than claiming that
one machine's crossover is universal.

For fixed-cost geometries, start with per-geometry point thresholds. For variable
geometry and collections, evaluate an inexpensive work estimate such as points
times segments/faces or a weighted source cost. Only introduce that estimate if
it improves measured decisions and uses already available metadata; avoid new
geometry scans or assembly rebuilds for dispatch. Otherwise retain conservative
detachment for those cases, including expensive single-point work.

### Sensor read policy

Do not apply the ordinary batch point threshold directly to an individual sensor
read: it always requests one field point. Benchmark a source-work estimate for
Mesh, Path, Sheet, and source collections. Keep cheap single-source reads attached
unless measurement shows a benefit; detach expensive one-point reads when both
latency and Python-thread responsiveness justify the clone or preparation cost
needed to make the Rust work independent of borrowed Python references.

For `ObserverCollection.read_all()`, stage all Python-owned state while attached,
perform only Rust-owned work while detached, then convert outputs and synchronize
state after reattachment. The preferred implementation should evaluate all sensor
positions through one `compute_B_batch()` call and apply the sensor transfer
functions to the resulting fields. This reuses Magba's batch dispatch and avoids
calling `source.compute_B()` once per sensor. Include staging and result conversion
in the end-to-end timing even though they remain attached.

Preserve observable ordering and HallLatch hysteresis. A latch result must update
the authoritative Python child exactly once in collection order. Repeated references
to the same latch need deterministic sequential semantics; exclude that case from
parallel post-processing unless equivalence is proven. If batched field evaluation
requires new Magba APIs for applying a sensor to a precomputed field, coordinate
that interface in the separate Magba PR. Retain the current sequential path until
the batched path has equivalent state behavior.

## 4. Integrate the selected policy

- Add a private `src/execution.rs` module for named detach thresholds and shared
  decision logic. Use it from `src/fields.rs`, `src/macros.rs`, and
  `src/collection.rs`; use it from sensor wrappers where source-work detachment is
  supported, and register it in `src/lib.rs`.
- Keep functional and object policies consistent by default. Introduce separate
  cutoffs only when repeated measurements show a meaningful difference.
- Keep argument extraction, Python object access, and NumPy result construction
  attached. Detach only the Rust work already supported by the existing borrowing
  and ownership model.
- Feed supported Rayon recommendations into Magba's threshold configuration or
  generator through a reviewed change. Benchmark the integrated values; do not
  infer benefit from a report alone or vendor Magba solely for calibration.
- Preserve raw evidence and a compact checked-in results summary with commands
  needed to reproduce it. Reject incomplete, inconclusive, or mismatched result
  sets before updating constants. Never retune automatically during installation
  or import.
- Treat free-threaded Python as a separate validation target; retain/detach
  semantics still matter, but conventional GIL timing conclusions do not transfer
  automatically.

## 5. Verify correctness and guard performance

Add focused tests for forced-mode selection and policy boundaries: empty and
singleton inputs, threshold minus one, threshold, and threshold plus one. Compare
numerical outputs, shapes, and exceptions across modes; exercise noncontiguous
inputs and collection cache invalidation. Test any work estimate for overflow and
expensive singleton behavior.

For sensors, compare unified and specialized reads across retained and detached
paths. Verify `ObserverCollection.read_all()` output types and order, collection
pose application, child mutation visibility, source-collection reads, empty input,
and repeated sensor references. Add explicit HallLatch tests for activation,
release, repeated reads, and authoritative child-state synchronization.

Extend the existing GIL responsiveness test in
`python/tests/functions/test_arraylike.py` to cover the changed collection and
variable-geometry policies where applicable. Add a responsiveness case for a large
observer collection or expensive sensor source. Keep timing-sensitive speedup
assertions out of correctness tests.

Expand `benchmarks/benchmarks_ffi.py` and the pytest benchmark suites in
`python/benchmarks/` with representative small batches and cutover-adjacent sizes.
Keep the full calibration sweep opt-in; CI should run a small regression subset.
Use actual wall-clock measurements for Rayon calibration.

Run release-build Python tests, Rust checks/tests for changed policy code, lint,
and stub consistency checks. Verify a normal wheel has no calibration exports or
active overrides. Report before/after timings for small, transition, and large
batches. Investigate any repeatable regression above 5% before accepting new
defaults; preserve the current policy where evidence is insufficient.

## Delivery sequence and completion criteria

1. Add and verify calibration controls, coordinating the Magba interface.
2. Add the harness and record an unchanged-policy baseline.
3. Calibrate and review candidate policies; retain evidence for rejected or
   inconclusive cases.
4. Integrate selected values and shared detach decisions, then rebuild and measure
   the normal production configuration.
5. Add regression coverage and document results and reproduction commands.

Complete when the actual production build demonstrates repeatable benefits on
target workloads, preserves numerical behavior and Python responsiveness, and
includes reproducible evidence for every changed threshold. No numerical
threshold values are prescribed before measurement.

## Implementation status

The first calibration-control milestone is implemented on `perf-ffi-threshold`:

- Magba's calibration feature can force serial or parallel execution through
  batch, sum, and source-assembly dispatches.
- PyMagba's calibration feature can force GIL retention or detachment through
  functional fields, source objects, source collections, individual sensor
  methods, and `ObserverCollection.read_all()`.
- Optional branch counters verify the selected paths and remain disabled while
  measuring. Calibration controls and private Python exports are absent from
  normal builds.
- Detached sensor reads clone Python-owned sources before releasing the GIL.
  Observer collections stage sensors and synchronize latch state in collection
  order, preserving repeated-reference hysteresis.

The initial calibration harness is implemented in
`benchmarks/calibrate_thresholds.py`. It runs policies in isolated workers,
checks numerical equivalence and branch selection before timing, covers all
field/source APIs plus individual and collection sensor reads, varies source
complexity, preserves raw samples and provenance, and reports only stable
neighboring-size crossover candidates. It now follows observed advantages with
a focused second pass at intermediate and adjacent work sizes. GIL comparisons
also record a separate sleeping-thread progress probe, marking calls shorter than
the required interior sampling window as inconclusive. Input-layout validation,
batched observer-collection optimization, measured threshold selection, and
production-policy integration remain pending.
