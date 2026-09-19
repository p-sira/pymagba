# Performance Comparison: PyMagba vs Magpylib

This document provides a comprehensive performance comparison between `pymagba` (v0.6.0) and `magpylib` (v5.2.2).

We evaluate the libraries across several key metrics:
1. **Pure Field Function Performance** (Raw mathematical field computation)
2. **Collection Performance** (Aggregated object field computation)
3. **Object Creation** (Instantiating magnet and current objects)
4. **Object Manipulation** (Translation, rotation, and spatial transformations)

## 1. Pure Field Function Performance

The pure field computation is the core bottleneck in most magnetic simulations. `pymagba` leverages Rust's performance and aggressive optimizations to significantly accelerate these calculations compared to `magpylib`. 

Below is a comparison of computation times for various source geometries, calculated over 1,000,000 observer positions:

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Cylinder** | 65.09 ms | 1488.58 ms | 22.9x | 2.16e-09 | 2.28e-12 |
| **Sphere** | 21.20 ms | 369.89 ms | 17.5x | 2.65e-15 | 1.02e-15 |
| **Cuboid** | 84.72 ms | 1345.54 ms | 15.9x | 1.36e-12 | 2.64e-13 |
| **Dipole** | 21.32 ms | 268.53 ms | 12.6x | 2.81e-15 | 9.93e-16 |
| **Tetrahedron** | 71.31 ms | 3851.05 ms | 54.0x | 6.07e-08 | 2.76e-11 |
| **Mesh** | 71.95 ms | 7039.98 ms | 97.8x | 6.07e-08 | 2.76e-11 |
| **Circular** | 32.97 ms | 583.43 ms | 17.7x | 3.46e-15 | 1.04e-15 |
| **Polyline** | 35.09 ms | 2309.02 ms | 65.8x | 2.34e-12 | 1.06e-14 |
*(Note: The above benchmarks are executed using `asv` via our `benchmarks/` suite).*

## 2. Collection Performance

Evaluating the performance of field computation for a collection of objects over 1,000,000 observer positions:

| Operation | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|-----------|--------------|---------------|---------|----------------|----------------|
| **Collection** | 137.03 ms | 2373.60 ms | 17.3x | 3.37e-12 | 4.68e-16 |
## 3. Object Creation

Creating objects in bulk or iteratively can introduce overhead. Here we compare the time taken to instantiate 10,000 objects such as `Cuboid`, `Cylinder`, etc.

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cuboid | 346.23 ms | 813.76 ms | 2.4x |
| Cylinder | 340.25 ms | 817.68 ms | 2.4x |
| Collection | 66.66 ms | 2343.81 ms | 35.2x |
## 4. Object Manipulation

Simulations often require dynamic movement of sources. This benchmark measures the overhead of translating and rotating objects in 3D space (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Translate | 2.36 ms | 340.71 ms | 144.3x |
| Rotate | 30.57 ms | 2853.98 ms | 93.4x |
---

## Reproducing these Benchmarks

These benchmarks were executed on the following environment:
- **OS:** Linux 6.19.6-arch1-1
- **CPU:** AMD Ryzen 5 4600H with Radeon Graphics (12 cores)
- **RAM:** 16 GB
- **Python:** 3.12

To reproduce these benchmarks on your local machine, run the `asv` suite provided in the repository:

```bash
asv run
```