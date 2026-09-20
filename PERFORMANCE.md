# Performance Comparison: PyMagba vs Magpylib

This document provides a comprehensive performance comparison between `pymagba` v0.6.0 and `magpylib` v5.2.2.

## 1. Field Computation Performance

The pure field computation is the core bottleneck in most magnetic simulations. `pymagba` leverages Rust's performance and aggressive optimizations to significantly accelerate these calculations. 

Below is a comparison of computation times for various source geometries, calculated over 1,000,000 observer positions. `Collection` consists of 3 magnets, a cylinder, cuboid, and a dipole.

### Magnets

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Cylinder** | *TBD* | *TBD* | *TBD* | 2.16e-09 | 2.28e-12 |
| **Sphere** | *TBD* | *TBD* | *TBD* | 2.65e-15 | 1.02e-15 |
| **Cuboid** | *TBD* | *TBD* | *TBD* | 1.36e-12 | 2.64e-13 |
| **Dipole** | *TBD* | *TBD* | *TBD* | 2.81e-15 | 9.93e-16 |
| **Tetrahedron** | *TBD* | *TBD* | *TBD* | 6.07e-08 | 2.76e-11 |
| **Mesh** | *TBD* | *TBD* | *TBD* | 6.07e-08 | 2.76e-11 |
| **Triangle** | 29.00 ms | 4658.11 ms | 160.6x | 1.11e+00 | 5.36e-14 |

### Currents

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Circular** | *TBD* | *TBD* | *TBD* | 3.68e-15 | 1.10e-15 |
| **Polyline** | *TBD* | *TBD* | *TBD* | 2.34e-12 | 1.06e-14 |
| **TriangleCurrent** | 38.43 ms | 11570.01 ms | 301.1x | 5.00e-10 | 1.65e-13 |
| **SheetCurrent** | 101.57 ms | 22312.15 ms | 219.7x | 1.28e-09 | 3.83e-13 |

### Composite

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Collection** | *TBD* | *TBD* | *TBD* | 3.37e-12 | 4.68e-16 |

## 2. Object Creation

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cylinder | *TBD* | *TBD* | *TBD* |
| Collection | *TBD* | *TBD* | *TBD* |

## 3. Object Manipulation

Simulations often require dynamic movement of sources. This benchmark measures the overhead of translating and rotating objects in 3D space (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Translate Cylinder | *TBD* | *TBD* | *TBD* |
| Rotate Cylinder | *TBD* | *TBD* | *TBD* |
| Translate Collection | *TBD* | *TBD* | *TBD* |
| Rotate Collection | *TBD* | *TBD* | *TBD* |

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