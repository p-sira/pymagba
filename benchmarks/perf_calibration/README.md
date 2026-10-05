# Performance Calibration

PyMagba makes two separate performance decisions for magnetic-field work:

1. Magba decides whether Rust should process a batch serially or with Rayon.
2. PyMagba decides whether to detach the calling thread from Python while Rust
   performs the work. On GIL-enabled Python builds, detaching lets other Python
   threads run.

Both operations have overhead, so they are not automatically faster for small
workloads. The defaults are calibrated on a reference machine and are intended
as reasonable general defaults, not optimal values for every machine. This
directory contains the reproducible workflow, report extractor, and reviewed
results.

- [`calibrate_thresholds.py`](calibrate_thresholds.py) runs the benchmark sweep.
- [`extract_thresholds.py`](extract_thresholds.py) converts report JSON into
  Markdown tables or machine-readable JSON.
- [`RESULTS.md`](RESULTS.md) documents the reviewed calibration run and the
  thresholds selected from it.

## Calibration Feature

The non-default Cargo feature `threshold-calibration` exposes private controls
used only by the benchmark. It can independently force:

- Magba execution to `auto`, `serial`, or `parallel`.
- PyMagba interpreter handling to `auto`, `retain`, or `detach`.

Branch counters verify that each sample used the requested path. These controls
are absent from normal builds and do not change the public Python API.

## Run a Calibration

From the repository root, build the release extension with the calibration
feature. Then verify every selected policy and inspect the planned workload:

```console
uv run maturin develop --release --features threshold-calibration
uv run python benchmarks/perf_calibration/calibrate_thresholds.py --preflight
uv run python benchmarks/perf_calibration/calibrate_thresholds.py --dry-run
```

Run the complete sweep on an otherwise idle machine:

```console
RAYON_NUM_THREADS=12 uv run python \
  benchmarks/perf_calibration/calibrate_thresholds.py \
  --policy-rounds 5 \
  --results-dir benchmark-results
```

Set `RAYON_NUM_THREADS` explicitly for reproducible results. If it is unset,
Rayon uses the parallelism available to the process, normally the number of
visible logical CPUs after affinity or container restrictions.

The default run covers all field kernels, functional and object APIs, geometry
complexity, source collections, sensor methods, observer collections, input
layouts, and alternate point distributions. Policies run in isolated processes
and balanced rotating order. Interactive terminals show `tqdm` progress; pass
`--no-progress` to suppress it.

Each run creates a timestamped directory containing:

- one checkpoint per policy, phase, and round;
- raw samples and summarized medians;
- Rayon and GIL crossover candidates;
- validation results and explicit search-limit reasons;
- CPU, toolchain, extension, repository, and thread-count provenance;
- a final `report.json`.

The output directory is ignored by Git because reports are large and
machine-specific. Preserve any report needed for review before cleaning the
workspace.

## View or Export Results

Print a report as Markdown:

```console
uv run python benchmarks/perf_calibration/extract_thresholds.py \
  benchmark-results/ffi-threshold-*/report.json
```

Extract only Rayon candidates or write JSON for other tooling:

```console
uv run python benchmarks/perf_calibration/extract_thresholds.py \
  benchmark-results/ffi-threshold-*/report.json \
  --comparison rayon \
  --format json \
  --output benchmark-results/thresholds.json
```

For each non-collection kernel, the extractor's summary selects the largest
stable crossover across its detailed workloads, including functional and object
APIs. This favors the later, safer transition when workloads disagree. Supply
only reports from the calibration set under review; combining different
machines or thread counts does not produce a meaningful threshold.

The reviewed run is summarized in [`RESULTS.md`](RESULTS.md). Its generated
extraction is available in [generated_results.md](generated_results.md).

## Interpreting Results

Rayon and GIL results answer different questions and should be reviewed
separately:

- The **Rayon comparison** keeps Python handling fixed and compares forced
  serial and forced parallel Rust execution. It finds when useful computation
  repays Rayon's scheduling and reduction overhead.
- The **GIL comparison** uses Magba's automatic Rust dispatch and compares
  retaining and detaching the Python thread state. It measures call latency;
  the responsiveness probe separately checks whether another Python thread can
  make progress during a sufficiently long call.

### Candidate Status

Each candidate group has one of three statuses:

- `crossover` means the right-hand policy was at least 5% faster at two adjacent
  tested work sizes and won at least two-thirds of sample comparisons;
- `inconclusive` means at least one size qualified, but adjacent evidence did
  not confirm a stable transition;
- `no_crossover` means no tested size met the required advantage.

Use `maximum_tested_work_size` and `search_limit_reason` to distinguish a
negative result from a sweep that simply stopped too early. Do not turn an
`inconclusive` or `no_crossover` result into a threshold by using the largest
tested size.

### First Parallel Size and Stored Threshold

For fixed-cost kernels, reports identify the first point count supporting the
parallel policy. Rust and PyMagba use the strict condition `len > threshold`, so
the stored point threshold is one less. For example, a first parallel size of
160 produces a threshold of 159: sizes through 159 stay serial, and size 160
uses Rayon.

The extractor displays both values, but this point-count conversion is literal
only for fixed-cost kernels. Its summary is a review aid, not a source-code
patch.

### Workload Shape and Complexity

Mesh, Path, and Sheet work depends on both point count and the number of active
faces or segments. Magba therefore converts a calibrated total-work threshold
into a point threshold at runtime. More expensive geometry can profit from
parallelism at fewer points; choosing a later crossover across fixtures protects
cheaper geometry from premature parallelization. This adaptive calculation
controls Rayon's execution; PyMagba makes its GIL-detachment decision
separately.

`SourceCollection` uses a separate model. Magba sums each child's relative
complexity, including nested collections, and considers approximately
`point_count * total_relative_complexity`. It parallelizes across the
collection's direct children only when there is more than one direct child and
the work estimate exceeds the collection threshold. Consequently, a single
point-only constant cannot describe collection behavior. Review the detailed
homogeneous, mixed, and nested collection rows independently. PyMagba's
GIL-detachment rule is separate and currently detaches collection field calls
containing more than one observation point.

Layout and point-distribution validations are supporting evidence around an
already measured transition. Conversion-heavy Python lists or `float32` inputs
can hide an end-to-end improvement and should not replace the primary
contiguous-`float64` kernel comparison.

### Sensors and Responsiveness

An individual sensor evaluates one field point, so its work axis is source
complexity rather than batch length. Observer collections scale with both sensor
count and source complexity. Forced sensor detachment also has cloning and
staging costs. A missing crossover means those costs were not recovered in the
tested range; it does not justify applying a field-batch threshold to sensor
reads. Production sensor reads currently remain attached to Python.

A responsiveness result of `too_short` means the call ended before the probe
could measure it, not that Python was retained. For long calls, responsiveness
may justify detachment even when isolated call latency is similar.

### Comparing Runs

Only combine reports with compatible CPU affinity, Rayon thread count, compiler
settings, Python mode, and benchmark configuration. Check the provenance stored
in each report. Recalibrate when these conditions differ materially.

## Return to a Normal Build

After calibration, reinstall PyMagba without the private benchmarking feature:

```console
uv run maturin develop --release
```

Thresholds are compile-time defaults. PyMagba does not run calibration during
import, installation, or ordinary API calls.
