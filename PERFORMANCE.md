# Performance Comparison: PyMagba vs Magpylib

This document provides a comprehensive performance comparison between `pymagba` v0.6.0 and `magpylib` v5.2.2.

## 1. Field Computation Performance

The pure field computation is the core bottleneck in most magnetic simulations. `pymagba` leverages Rust's performance and aggressive optimizations to significantly accelerate these calculations. 

Below is a comparison of computation times for various source geometries, calculated over 1,000,000 observer positions. `Collection` consists of 3 magnets, a cylinder, cuboid, and a dipole.

### Magnets

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Cylinder** | 61.00 ms | 1318.89 ms | 21.6x | 2.16e-09 | 2.28e-12 |
| **Sphere** | 20.30 ms | 347.37 ms | 17.1x | 2.65e-15 | 1.02e-15 |
| **Cuboid** | 76.75 ms | 1213.42 ms | 15.8x | 1.36e-12 | 2.64e-13 |
| **Dipole** | 20.47 ms | 247.42 ms | 12.1x | 2.81e-15 | 9.93e-16 |
| **Tetrahedron** | 66.39 ms | 3485.68 ms | 52.5x | 6.07e-08 | 2.76e-11 |
| **Mesh** | 65.71 ms | 6871.90 ms | 104.6x | 6.07e-08 | 2.76e-11 |
| **Triangle** | 29.63 ms | 690.72 ms | 23.3x | 1.78e-10 | 5.64e-14 |

### Currents

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Circular** | 30.29 ms | 500.75 ms | 16.5x | 3.68e-15 | 1.10e-15 |
| **Polyline** | 34.31 ms | 2088.60 ms | 60.9x | 2.34e-12 | 1.06e-14 |
| **TriangleCurrent** | 38.33 ms | 11536.54 ms | 301.0x | 5.00e-10 | 1.65e-13 |
| **SheetCurrent** | 99.56 ms | 22281.83 ms | 223.8x | 1.28e-09 | 3.83e-13 |

### Composite

| Geometry Type | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|---------------|--------------|---------------|---------|----------------|----------------|
| **Collection** | 122.92 ms | 2115.00 ms | 17.2x | 3.37e-12 | 4.68e-16 |

## 2. Object Creation

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cylinder | 326.66 ms | 771.01 ms | 2.4x |
| Collection | 34.93 ms | 1819.90 ms | 52.1x |

## 3. Object Manipulation

Simulations often require dynamic movement of sources. This benchmark measures the overhead of translating and rotating objects in 3D space (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Translate Cylinder | 2.10 ms | 83.81 ms | 39.9x |
| Rotate Cylinder | 10.59 ms | 510.22 ms | 48.2x |
| Translate Collection | 2.30 ms | 253.39 ms | 110.3x |
| Rotate Collection | 10.74 ms | 2142.18 ms | 199.5x |

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