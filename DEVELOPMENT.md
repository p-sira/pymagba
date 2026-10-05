# Development & Reproducibility

## Building from Source

Clone into the repository:

```shell
git clone https://github.com/p-sira/pymagba.git
cd pymagba
```

Set up git hooks:

```shell
chmod +x scripts/setup_git_hooks.sh && scripts/setup_git_hooks.sh
```

To reproduce the build:

```shell
uv sync --group dev
cargo stub-gen
maturin build --release
```

Installing the build:

```shell
pip install target/wheels/pymagba-*.whl
```

Generating the docs:

```shell
uv sync --group dev
mkdir docs
cd docs
make html
```

To verify the installation and the generated stubs:

```shell
uv run pytest
uv run mypy python/pymagba
```

To verify the completeness of the generated stubs:

```shell
uv run pytest python/tests/test_stubs.py
```

## Performance

You can benchmark the performance of PyMagba using:

```shell
uv run pytest bench
```

Then, extract the benchmark results to a comprehensive format in [PERFORMANCE.md](PERFORMANCE.md):

```shell
uv run python scripts/collate_benchmarks.py
```

For advanced users who wish to best optimize for their specific machine, see the [performance calibration guide](benchmarks/perf_calibration/README.md) for the complete procedure.
