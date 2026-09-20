# Performance Comparison: PyMagba vs Magpylib

This document provides a comprehensive performance comparison between `pymagba` v0.6.0 and `magpylib` v5.2.2.

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
| **Cylinder** | *TBD* | *TBD* | *TBD* | 2.16e-09 | 2.28e-12 |
| **Sphere** | *TBD* | *TBD* | *TBD* | 2.65e-15 | 1.02e-15 |
| **Cuboid** | *TBD* | *TBD* | *TBD* | 1.36e-12 | 2.64e-13 |
| **Dipole** | *TBD* | *TBD* | *TBD* | 2.81e-15 | 9.93e-16 |
| **Tetrahedron** | *TBD* | *TBD* | *TBD* | 6.07e-08 | 2.76e-11 |
| **Mesh** | *TBD* | *TBD* | *TBD* | 6.07e-08 | 2.76e-11 |
| **Circular** | *TBD* | *TBD* | *TBD* | 3.46e-15 | 1.04e-15 |
| **Polyline** | *TBD* | *TBD* | *TBD* | 2.34e-12 | 1.06e-14 |
## 2. Collection Performance

Evaluating the performance of field computation for a collection of objects over 1,000,000 observer positions:

| Operation | PyMagba Time | Magpylib Time | Speedup | Max Rel. Error | P95 Rel. Error |
|-----------|--------------|---------------|---------|----------------|----------------|
| **Collection** | *TBD* | *TBD* | *TBD* | 3.37e-12 | 4.68e-16 |
## 3. Object Creation

Creating objects in bulk or iteratively can introduce overhead. Here we compare the time taken to instantiate 10,000 objects such as `Cuboid`, `Cylinder`, etc.

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Cylinder | 335.49 ms | 782.42 ms | 2.3x |
| Collection | 35.17 ms | 1749.47 ms | 49.8x |
## 4. Object Manipulation

Simulations often require dynamic movement of sources. This benchmark measures the overhead of translating and rotating objects in 3D space (10,000 operations).

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Translate Cylinder | 2.00 ms | 84.43 ms | 42.3x |
| Rotate Cylinder | 30.15 ms | 496.11 ms | 16.5x |
| Translate Collection | 2.31 ms | 248.46 ms | 107.8x |
| Rotate Collection | 30.35 ms | 2013.04 ms | 66.3x |
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