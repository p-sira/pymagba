# Performance Comparison: PyMagba vs Magpylib

This document provides a comprehensive performance comparison between `pymagba` v0.6.0 and `magpylib` v5.2.2.

## 1. Field Computation Performance

The pure field computation is the core bottleneck in most magnetic simulations. `pymagba` leverages Rust's performance and aggressive optimizations to significantly accelerate these calculations. 

Below is a comparison of computation times for various source geometries, calculated over 1,000,000 observer positions. `Collection` consists of 3 magnets, a cylinder, cuboid, and a dipole.

### Magnets

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Cylinder** | 69.94 ms | 1346.61 ms | 19.3x | 2.16e-09 | 2.28e-12 |
| **Sphere** | 24.35 ms | 363.80 ms | 14.9x | 2.65e-15 | 1.02e-15 |
| **Cuboid** | 82.73 ms | 1233.30 ms | 14.9x | 1.36e-12 | 2.64e-13 |
| **Dipole** | 24.16 ms | 270.91 ms | 11.2x | 2.81e-15 | 9.93e-16 |
| **Tetrahedron** | 74.27 ms | 5303.20 ms | 71.4x | 6.07e-08 | 2.76e-11 |
| **Mesh** | 74.19 ms | 8443.25 ms | 113.8x | 6.07e-08 | 2.76e-11 |
| **Triangle** | 33.36 ms | 4650.80 ms | 139.4x | 1.78e-10 | 5.64e-14 |

### Currents

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Circular** | 36.26 ms | 525.72 ms | 14.5x | 3.68e-15 | 1.10e-15 |
| **Polyline** | 45.94 ms | 2146.41 ms | 46.7x | 2.34e-12 | 1.06e-14 |
| **TriangleCurrent** | 45.61 ms | 11509.41 ms | 252.4x | 5.00e-10 | 1.65e-13 |
| **SheetCurrent** | 109.97 ms | 23074.28 ms | 209.8x | 1.28e-09 | 3.83e-13 |

### Composite

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Collection** | 136.60 ms | 2161.66 ms | 15.8x | 3.37e-12 | 4.68e-16 |

## 2. Object Creation

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cylinder | 323.49 ms | 769.31 ms | 2.4x |
| Collection | 36.48 ms | 1777.74 ms | 48.7x |

## 3. Object Manipulation

Simulations often require dynamic movement of sources. This benchmark measures the overhead of translating and rotating objects in 3D space (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Translate Cylinder | 2.25 ms | 82.56 ms | 36.8x |
| Rotate Cylinder | 14.67 ms | 504.82 ms | 34.4x |
| Translate Collection | 2.46 ms | 250.85 ms | 102.2x |
| Rotate Collection | 11.29 ms | 2040.27 ms | 180.8x |

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