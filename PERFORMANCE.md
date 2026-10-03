# Performance Comparison: PyMagba vs Magpylib

This document provides a comprehensive performance comparison between `pymagba` v0.7.0 and `magpylib` v5.2.2.

## 1. Field Computation Performance

The pure field computation is the core bottleneck in most magnetic simulations. `pymagba` leverages Rust's performance and aggressive optimizations to significantly accelerate these calculations. 

Below is a comparison of computation times for various source geometries, calculated over 1,000,000 observer positions. `Collection` consists of 3 magnets, a cylinder, cuboid, and a dipole.

### Magnets

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Cylinder** | 48.79 ms | 1318.36 ms | 27.0x | 1.70e-09 | 1.96e-12 |
| **Sphere** | 6.36 ms | 344.35 ms | 54.1x | 2.23e-15 | 9.21e-16 |
| **Cuboid** | 65.03 ms | 1215.63 ms | 18.7x | 1.28e-12 | 2.56e-13 |
| **Dipole** | 6.27 ms | 247.11 ms | 39.4x | 2.34e-15 | 8.94e-16 |
| **Tetrahedron** | 55.09 ms | 4212.50 ms | 76.5x | 1.17e-06 | 2.53e-11 |
| **Mesh** | 56.35 ms | 7667.71 ms | 136.1x | 1.17e-06 | 2.53e-11 |
| **Triangle** | 17.04 ms | 687.34 ms | 40.3x | 1.78e-10 | 5.91e-14 |

### Currents

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Circular** | 14.32 ms | 506.89 ms | 35.4x | 3.90e-15 | 1.12e-15 |
| **Polyline** | 16.48 ms | 2115.33 ms | 128.4x | 1.17e-12 | 1.07e-14 |
| **TriangleCurrent** | 22.83 ms | 11615.76 ms | 508.8x | 5.00e-10 | 1.66e-13 |
| **SheetCurrent** | 74.53 ms | 24437.70 ms | 327.9x | 1.28e-09 | 3.81e-13 |

### Composite

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Collection** | 65.88 ms | 2136.40 ms | 32.4x | 2.04e-09 | 4.25e-10 |

## 2. Small-Batch / Looped Field Computation

In dynamic tracking and time-stepping simulations (such as sensor reading loops or trajectory integration), magnetic fields are frequently evaluated over small observer batches (1–10 positions) in a tight loop. This benchmark measures the per-call overhead, FFI boundary cost, and dispatch efficiency when evaluating 1 and 10 observer positions repeatedly (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cylinder (1 point) | 6.67 ms | 5793.30 ms | 868.8x |
| Cylinder (10 points) | 37.34 ms | 10383.75 ms | 278.1x |
| Cuboid (1 point) | 7.90 ms | 5013.92 ms | 634.9x |
| Cuboid (10 points) | 49.03 ms | 5373.29 ms | 109.6x |
| Dipole (1 point) | 3.23 ms | 2765.58 ms | 855.3x |
| Dipole (10 points) | 3.94 ms | 3024.16 ms | 767.1x |
| Collection (1 point) | 148.31 ms | 8517.87 ms | 57.4x |
| Collection (10 points) | 176.17 ms | 11700.30 ms | 66.4x |


## 3. Object Creation

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cylinder | 43.67 ms | 436.40 ms | 10.0x |
| Collection | 21.66 ms | 1789.42 ms | 82.6x |


## 4. Object Manipulation

Simulations often require dynamic movement of sources. This benchmark measures the overhead of translating and rotating objects in 3D space (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Translate Cylinder | 1.86 ms | 84.74 ms | 45.7x |
| Rotate Cylinder | 2.00 ms | 514.81 ms | 257.1x |
| Translate Collection | 1.86 ms | 256.58 ms | 137.9x |
| Rotate Collection | 2.03 ms | 2029.31 ms | 1001.4x |

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