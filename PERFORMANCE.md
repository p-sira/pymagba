# Performance Comparison: PyMagba vs Magpylib

This document provides a comprehensive performance comparison between `pymagba` v0.7.0 and `magpylib` v5.2.2.

## 1. Field Computation Performance

The pure field computation is the core bottleneck in most magnetic simulations. `pymagba` leverages Rust's performance and aggressive optimizations to significantly accelerate these calculations. 

Below is a comparison of computation times for various source geometries, calculated over 1,000,000 observer positions. `Collection` consists of 3 magnets, a cylinder, cuboid, and a dipole.

### Magnets

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Cylinder** | 56.00 ms | 1324.63 ms | 23.7x | 1.70e-09 | 1.96e-12 |
| **Sphere** | 12.07 ms | 346.41 ms | 28.7x | 2.65e-15 | 1.02e-15 |
| **Cuboid** | 69.74 ms | 1211.65 ms | 17.4x | 1.28e-12 | 2.64e-13 |
| **Dipole** | 14.62 ms | 246.66 ms | 16.9x | 2.81e-15 | 9.92e-16 |
| **Tetrahedron** | 56.54 ms | 3545.70 ms | 62.7x | 1.17e-06 | 2.79e-11 |
| **Mesh** | 71.22 ms | 6786.28 ms | 95.3x | 1.17e-06 | 2.79e-11 |
| **Triangle** | 23.63 ms | 680.15 ms | 28.8x | 1.78e-10 | 5.64e-14 |

### Currents

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Circular** | 23.66 ms | 499.59 ms | 21.1x | 3.90e-15 | 1.10e-15 |
| **Polyline** | 27.76 ms | 2085.12 ms | 75.1x | 1.17e-12 | 1.07e-14 |
| **TriangleCurrent** | 33.87 ms | 11533.87 ms | 340.6x | 5.00e-10 | 1.65e-13 |
| **SheetCurrent** | 100.38 ms | 22074.38 ms | 219.9x | 1.28e-09 | 3.81e-13 |

### Composite

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Collection** | 110.06 ms | 2129.66 ms | 19.3x | 3.37e-12 | 4.68e-16 |

## 2. Small-Batch / Looped Field Computation

In dynamic tracking and time-stepping simulations (such as sensor reading loops or trajectory integration), magnetic fields are frequently evaluated over small observer batches (1–10 positions) in a tight loop. This benchmark measures the per-call overhead, FFI boundary cost, and dispatch efficiency when evaluating 1 and 10 observer positions repeatedly (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cylinder (1 point) | 6.74 ms | 5894.25 ms | 874.8x |
| Cylinder (10 points) | 37.27 ms | 10269.92 ms | 275.6x |
| Cuboid (1 point) | 8.10 ms | 4920.00 ms | 607.7x |
| Cuboid (10 points) | 49.57 ms | 5617.48 ms | 113.3x |
| Dipole (1 point) | 3.67 ms | 2711.13 ms | 738.2x |
| Dipole (10 points) | 6.87 ms | 3080.50 ms | 448.7x |
| Collection (1 point) | 165.67 ms | 8438.63 ms | 50.9x |
| Collection (10 points) | 240.84 ms | 11571.48 ms | 48.0x |


## 3. Object Creation

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cylinder | 324.77 ms | 771.51 ms | 2.4x |
| Collection | 20.65 ms | 1787.85 ms | 86.6x |


## 4. Object Manipulation

Simulations often require dynamic movement of sources. This benchmark measures the overhead of translating and rotating objects in 3D space (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Translate Cylinder | 1.78 ms | 83.94 ms | 47.3x |
| Rotate Cylinder | 10.10 ms | 523.24 ms | 51.8x |
| Translate Collection | 1.81 ms | 264.18 ms | 145.9x |
| Rotate Collection | 10.01 ms | 2005.22 ms | 200.3x |

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