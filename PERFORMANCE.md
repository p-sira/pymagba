# Performance Comparison: PyMagba vs Magpylib

This document provides a comprehensive performance comparison between `pymagba` and `magpylib`. 

We evaluate the libraries across several key metrics:
1. **Pure Field Function Performance** (Raw mathematical field computation)
2. **Object Creation** (Instantiating magnet and current objects)
3. **Object Manipulation** (Translation, rotation, and spatial transformations)

## 1. Pure Field Function Performance

The pure field computation is the core bottleneck in most magnetic simulations. `pymagba` leverages Rust's performance and aggressive optimizations to significantly accelerate these calculations compared to `magpylib`. 

Below is a comparison of computation times for various source geometries, calculated over 1,000,000 observer positions:

| Geometry Type | PyMagba Time | Magpylib Time | Speedup |
|---------------|--------------|---------------|---------|
| **Cylinder**  | *TBD*        | *TBD*         | *TBD*x  |
| **Sphere**    | *TBD*        | *TBD*         | *TBD*x  |
| **Cuboid**    | *TBD*        | *TBD*         | *TBD*x  |
| **Dipole**    | *TBD*        | *TBD*         | *TBD*x  |
| **Circular**  | *TBD*        | *TBD*         | *TBD*x  |
| **Collection**| *TBD*        | *TBD*         | *TBD*x  |

*(Note: The above benchmarks are executed using `asv` via our `benchmarks/` suite).*

## 2. Object Creation

*(TODO: Add benchmark results for object creation)*

Creating objects in bulk or iteratively can introduce overhead. Here we compare the time taken to instantiate objects such as `Cuboid`, `Cylinder`, and `Sphere`.

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Instantiate 10,000 Cuboids | *TBD* | *TBD* | *TBD*x |
| Instantiate 10,000 Cylinders | *TBD* | *TBD* | *TBD*x |

## 3. Object Manipulation

*(TODO: Add benchmark results for spatial manipulation)*

Simulations often require dynamic movement of sources. This benchmark measures the overhead of translating and rotating objects in 3D space.

| Operation | PyMagba Time | Magpylib Time | Speedup |
|-----------|--------------|---------------|---------|
| Translate (10,000 operations) | *TBD* | *TBD* | *TBD*x |
| Rotate (10,000 operations)    | *TBD* | *TBD* | *TBD*x |

---

## Reproducing these Benchmarks

To reproduce these benchmarks on your local machine, run the `asv` suite provided in the repository:

```bash
asv run
```
