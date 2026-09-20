# Performance Comparison: PyMagba vs Magpylib

This document provides a comprehensive performance comparison between `pymagba` v0.6.0 and `magpylib` v5.2.2.

## 1. Field Computation Performance

The pure field computation is the core bottleneck in most magnetic simulations. `pymagba` leverages Rust's performance and aggressive optimizations to significantly accelerate these calculations. 

Below is a comparison of computation times for various source geometries, calculated over 1,000,000 observer positions. `Collection` consists of 3 magnets, a cylinder, cuboid, and a dipole.

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Cylinder** | 60.80 ms | 1313.59 ms | 21.6x | 2.16e-09 | 2.28e-12 |
| **Sphere** | 20.20 ms | 346.03 ms | 17.1x | 2.65e-15 | 1.02e-15 |
| **Cuboid** | 76.59 ms | 1204.16 ms | 15.7x | 1.36e-12 | 2.64e-13 |
| **Dipole** | 19.85 ms | 245.95 ms | 12.4x | 2.81e-15 | 9.93e-16 |
| **Tetrahedron** | 65.51 ms | 3568.64 ms | 54.5x | 6.07e-08 | 2.76e-11 |
| **Mesh** | 65.39 ms | 6791.74 ms | 103.9x | 6.07e-08 | 2.76e-11 |
| **Circular** | 29.07 ms | 499.40 ms | 17.2x | 3.46e-15 | 1.04e-15 |
| **Polyline** | 33.14 ms | 2095.33 ms | 63.2x | 2.34e-12 | 1.06e-14 |
| **Collection** | 121.71 ms | 2104.54 ms | 17.3x | 3.37e-12 | 4.68e-16 |

## 2. Object Creation

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cylinder | 315.40 ms | 770.36 ms | 2.4x |
| Collection | 34.50 ms | 1750.50 ms | 50.7x |

## 3. Object Manipulation

Simulations often require dynamic movement of sources. This benchmark measures the overhead of translating and rotating objects in 3D space (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Translate Cylinder | 2.15 ms | 93.07 ms | 43.4x |
| Rotate Cylinder | 10.60 ms | 585.56 ms | 55.3x |
| Translate Collection | 2.36 ms | 281.71 ms | 119.2x |
| Rotate Collection | 13.58 ms | 2125.53 ms | 156.6x |

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