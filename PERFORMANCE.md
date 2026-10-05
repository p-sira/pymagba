# Performance Comparison: PyMagba vs Magpylib

This document provides a comprehensive performance comparison between `pymagba` v0.7.0 and `magpylib` v5.2.2.

## 1. Field Computation Performance

The pure field computation is the core bottleneck in most magnetic simulations. `pymagba` leverages Rust's performance and aggressive optimizations to significantly accelerate these calculations. 

Below is a comparison of computation times for various source geometries, calculated over 1,000,000 observer positions. `Collection` consists of 3 magnets, a cylinder, cuboid, and a dipole.

### Magnets

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Cylinder** | 35.62 ms | 1307.98 ms | 36.7x | 2.59e-09 | 1.90e-12 |
| **Sphere** | 6.41 ms | 345.88 ms | 54.0x | 2.23e-15 | 9.21e-16 |
| **Cuboid** | 63.06 ms | 1207.65 ms | 19.2x | 1.28e-12 | 2.56e-13 |
| **Dipole** | 6.27 ms | 245.10 ms | 39.1x | 2.34e-15 | 8.94e-16 |
| **Tetrahedron** | 54.77 ms | 4185.22 ms | 76.4x | 1.17e-06 | 2.53e-11 |
| **Mesh** | 56.53 ms | 6982.19 ms | 123.5x | 1.17e-06 | 2.53e-11 |
| **Triangle** | 17.17 ms | 680.53 ms | 39.6x | 1.78e-10 | 5.91e-14 |

### Currents

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Circular** | 14.52 ms | 500.19 ms | 34.4x | 3.90e-15 | 1.12e-15 |
| **Polyline** | 16.91 ms | 2075.44 ms | 122.7x | 1.17e-12 | 1.07e-14 |
| **TriangleCurrent** | 22.81 ms | 11559.17 ms | 506.7x | 5.00e-10 | 1.66e-13 |
| **SheetCurrent** | 73.90 ms | 22071.20 ms | 298.6x | 1.28e-09 | 3.81e-13 |

### Composite

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Collection** | 58.48 ms | 2113.89 ms | 36.1x | 2.04e-09 | 4.25e-10 |

## 2. Small-Batch / Looped Field Computation

In dynamic tracking and time-stepping simulations (such as sensor reading loops or trajectory integration), magnetic fields are frequently evaluated over small observer batches (1–10 positions) in a tight loop. This benchmark measures the per-call overhead, FFI boundary cost, and dispatch efficiency when evaluating 1 and 10 observer positions repeatedly (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cylinder (1 point) | 5.83 ms | 5775.80 ms | 990.0x |
| Cylinder (10 points) | 28.36 ms | 10276.56 ms | 362.4x |
| Cuboid (1 point) | 8.16 ms | 5025.50 ms | 616.1x |
| Cuboid (10 points) | 49.72 ms | 5400.59 ms | 108.6x |
| Dipole (1 point) | 3.32 ms | 2781.35 ms | 837.5x |
| Dipole (10 points) | 3.98 ms | 3048.93 ms | 766.8x |
| Collection (1 point) | 9.97 ms | 8474.41 ms | 850.1x |
| Collection (10 points) | 36.53 ms | 11618.83 ms | 318.1x |


## 3. Object Creation

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cylinder | 37.22 ms | 423.90 ms | 11.4x |
| Collection | 21.26 ms | 1776.01 ms | 83.6x |


## 4. Object Manipulation

Simulations often require dynamic movement of sources. This benchmark measures the overhead of translating and rotating objects in 3D space (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Translate Cylinder | 1.80 ms | 87.51 ms | 48.5x |
| Rotate Cylinder | 2.05 ms | 513.74 ms | 250.7x |
| Translate Collection | 1.75 ms | 254.93 ms | 145.8x |
| Rotate Collection | 2.06 ms | 2025.66 ms | 985.1x |

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

This report is generated using `scripts/collate_benchmarks.py`.