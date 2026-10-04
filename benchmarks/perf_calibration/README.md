# Performance Calibration

PyMagba uses calibrated thresholds to decide when a magnetic-field batch should
switch from serial execution to Rayon and when the Python interpreter can be
released for that work. This directory contains the reproducible calibration
workflow, the report extractor, and the curated results for the current target
machine.

- [`calibrate_thresholds.py`](calibrate_thresholds.py) runs the benchmark sweep.
- [`extract_thresholds.py`](extract_thresholds.py) converts report JSON into a
  readable Markdown table or machine-readable JSON.
- [`RESULTS.md`](RESULTS.md) records the reviewed production thresholds and
  their measured transition gains.

## Calibration Feature

The non-default Cargo feature `threshold-calibration` adds private controls for
benchmarking only. It can independently force:

- Magba execution to `auto`, `serial`, or `parallel`;
- PyMagba interpreter handling to `auto`, `retain`, or `detach`.

It also provides branch counters so every benchmark can verify the path it
actually measured. These controls are not exported by normal PyMagba builds and
do not change the public Python API.

## Run a Calibration

From the repository root, build the release extension with the calibration
feature and verify every selected policy:

```console
uv run maturin develop --release --features threshold-calibration
uv run python benchmarks/perf_calibration/calibrate_thresholds.py --preflight
uv run python benchmarks/perf_calibration/calibrate_thresholds.py --dry-run
```

Run the complete sweep:

```console
RAYON_NUM_THREADS=12 uv run python \
  benchmarks/perf_calibration/calibrate_thresholds.py \
  --policy-rounds 5 \
  --results-dir benchmark-results
```

Set `RAYON_NUM_THREADS` explicitly when producing reproducible results. If it is
unset, Rayon uses Rust's available parallelism: the logical CPUs visible to the
process after affinity or container restrictions.

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

The output directory is ignored by Git because reports are large and specific to
one machine. Preserve reports needed for review outside disposable workspaces.

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

The extractor's conservative Rayon recommendation is the largest stable
functional/object crossover for each kernel among the supplied reports. Pass
only reports from the calibration set being reviewed; mixing runs from different
machines or thread counts produces a combined recommendation and is usually not
meaningful. Treat collection and variable-complexity workloads separately before
changing constants.

The reviewed results currently used by the source code are easier to read in
[`RESULTS.md`](RESULTS.md).

## Interpreting Results

Rayon and GIL results answer different questions and should be reviewed
separately:

- The **Rayon comparison** holds GIL handling constant and compares forced
  serial against forced parallel Rust execution. It determines when parallel
  computation repays Rayon scheduling overhead.
- The **GIL comparison** uses automatic Rust dispatch and compares retaining
  against detaching the interpreter. It considers Python-call latency, while the
  responsiveness probe separately records whether another Python thread can
  progress during a sufficiently long call.

### Candidate Status

Each candidate group has one of three statuses:

- `crossover` means the right-hand policy was at least 5% faster in at least
  two neighboring work sizes and won at least two-thirds of paired samples;
- `inconclusive` means an isolated size qualified but neighboring evidence did
  not confirm a stable transition;
- `no_crossover` means no tested size met the required advantage.

`maximum_tested_work_size` and `search_limit_reason` distinguish an actual
negative result from a sweep that stopped before finding a stable transition.
Do not convert `inconclusive` or `no_crossover` into a threshold by using the
largest tested size.

### First Parallel Size and Stored Threshold

Reports express a candidate as the first work size where the parallel policy is
supported. The Rust and PyMagba dispatch conditions use `len > threshold`, so
the stored constant is normally one less. For example, a first parallel size of
160 corresponds to a stored threshold of 159: sizes through 159 remain serial,
and size 160 switches to Rayon.

The extraction script shows both values. Its conservative summary chooses the
largest stable functional/object crossover for each fixed kernel represented in
the supplied reports. This aggregation is a starting point for review, not an
automatic source-code update.

### Workload Shape and Complexity

Mesh, Path, and Sheet cost depends on faces or segments as well as point count.
SourceCollection cost also depends on child types, nesting, and source count.
Review their detailed rows instead of assuming that a point-only summary applies
to every workload. A conservative production value can deliberately delay
parallelism for expensive geometries to avoid regressing cheaper ones.

Layout and point-distribution validation is supporting evidence around an
already measured transition. Conversion-heavy Python lists or `float32` inputs
can dilute an end-to-end percentage improvement, but should not silently replace
the primary contiguous-`float64` kernel comparison.

### Sensors and Responsiveness

An individual sensor evaluates one field point, so its work axis is source
complexity rather than batch length. Observer collections use sensor count plus
source complexity. A missing sensor crossover means the cloning and staging cost
of detachment was not recovered in the measured range; it does not imply that
the ordinary field-batch threshold should be applied to sensor reads.

Treat a responsiveness result marked `too_short` as unmeasurable, not as proof
that the GIL was retained. For long computations, interpreter responsiveness can
justify detachment even when isolated call latency is similar.

### Comparing Runs

Only combine reports produced with compatible CPU affinity, Rayon thread count,
compiler settings, Python mode, and benchmark configuration. Check report
provenance before comparing thresholds. Recalibrate rather than transplanting
the current values when those conditions differ materially.

## Return to a Normal Build

After calibration, reinstall PyMagba without the private feature:

```console
uv run maturin develop --release
```

Thresholds are compile-time defaults. PyMagba never calibrates during import,
installation, or an ordinary user call.
