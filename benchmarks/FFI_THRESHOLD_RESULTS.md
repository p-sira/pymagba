# FFI threshold calibration results

## Target machine

These production defaults were calibrated on 2026-10-04 on Linux x86-64 with
12 logical CPUs visible to Rayon, Python 3.14.7, Rust 1.98.1, and the release
profile (`opt-level=3`, fat LTO, one codegen unit). `RAYON_NUM_THREADS` was
unset, so Rayon used the process's available parallelism: 12 threads.

The broad discovery run contains 3,967 calibration records and 1,082 layout
and point-distribution validation records. Its raw JSON remains in the ignored
`benchmark-results/ffi-threshold-20261004-114138-158316/` directory.

## Selected policy

The first discovery run exposed policy-process order drift, including an
impossible functional/object disagreement for the same Dipole kernel. The
harness now repeats each isolated policy in balanced rotating order and pools
samples across rounds. Five-round focused sweeps around every transition were
used for the final constants. A candidate had to beat serial execution by at
least 5% at neighboring sizes; the shared functional/object threshold uses the
more conservative supported transition.

The table lists the first point count that uses Rayon and releases the GIL.
The Rust and Python constants are one less because dispatch uses `len > threshold`.
The gain range is the median Rayon improvement across the tested APIs, variants,
and complexity fixtures at that point.

| Kernel | First parallel/detached size | Rayon gain at transition |
| --- | ---: | ---: |
| Circular current | 1,024 | 32.3-33.0% |
| Cuboid magnet | 160 | 27.9-28.5% |
| Cylinder magnet | 768 | 34.1-61.3% |
| Dipole | 24,576 | 23.1-27.8% |
| Mesh magnet | 16 | 15.0-62.1% |
| Path current | 410 | 21.5-74.9% |
| Sheet current | 48 | 47.3-54.9% |
| Sphere magnet | 24,576 | 12.0% |
| Tetrahedron magnet | 160 | 26.2-35.5% |
| Triangle magnet | 819 | 38.6-42.2% |
| Triangle current | 256 | 11.4-15.7% |

Mesh, Path, and Sheet cost also depends on faces or segments. Their defaults
use the slower transition from the low-complexity fixture, preventing premature
parallelization while accepting that high-complexity inputs could profit from
Rayon sooner. Source collections retain their existing policy because their
crossover varies strongly with child type, count, and nesting; a point-only
constant would be misleading.

Individual sensor reads and `ObserverCollection.read_all()` remain attached.
Across cheap sources, variable-complexity Path and Sheet sources, source
collections, sensor counts, and latch transitions, detachment produced no stable
sensor crossover. The cloning/staging path remains calibration-only so it can be
revisited without changing the public API.

Final automatic-policy checks covered the cutoff and first parallel point for
both functional and object APIs, both cylinder variants, and both variable-cost
fixtures. All 60 checks selected serial plus GIL retention at the cutoff and
Rayon plus GIL detachment above it.

## Reproduction

```console
uv run maturin develop --release --features threshold-calibration
RAYON_NUM_THREADS=12 uv run python benchmarks/calibrate_thresholds.py \
  --policy-rounds 5 --results-dir benchmark-results
```

These values are machine-optimized defaults, not architecture-independent
constants. Repeat the calibration for a materially different CPU, affinity,
Rayon thread count, compiler, or free-threaded Python build.
