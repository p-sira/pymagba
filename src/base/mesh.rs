/*
 * PyMagba is licensed under The 3-Clause BSD, see LICENSE.
 * Copyright 2025 Sira Pornsiriprasert <code@psira.me>
 */

use std::sync::{Arc, Mutex};

use nalgebra::Vector3;
use pyo3::prelude::*;

const MAX_CACHE_ENTRIES: usize = 8;
const MAX_TOTAL_FACES: usize = 200_000;
const MAX_SINGLE_MESH_FACES: usize = 150_000;
const MAX_FINGERPRINT_SAMPLES: usize = 64;

struct MeshCacheEntry {
    fingerprint: (u64, u64),
    num_verts: usize,
    num_faces: usize,
    trimesh: Arc<magba::base::mesh::TriMesh<f64>>,
}

struct MeshCache {
    entries: Vec<MeshCacheEntry>,
}

impl MeshCache {
    fn total_faces(&self) -> usize {
        self.entries.iter().map(|e| e.num_faces).sum()
    }
}

static MESH_CACHE: std::sync::LazyLock<Mutex<MeshCache>> = std::sync::LazyLock::new(|| {
    Mutex::new(MeshCache {
        entries: Vec::new(),
    })
});

fn sample_slice<T, F>(slice: &[T], max_samples: usize, mut hash_fn: F)
where
    F: FnMut(&T),
{
    if slice.is_empty() {
        return;
    }
    if slice.len() <= max_samples {
        for item in slice {
            hash_fn(item);
        }
    } else {
        let step = slice.len() / max_samples;
        for i in 0..max_samples {
            hash_fn(&slice[i * step]);
        }
        hash_fn(&slice[slice.len() - 1]);
    }
}

pub fn compute_mesh_fingerprint(verts: &[Vector3<f64>], faces: &[[usize; 3]]) -> (u64, u64) {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    let mut h1 = DefaultHasher::new();
    let mut h2 = DefaultHasher::new();

    // Distinct 64-bit salt constants for independence
    0x517cc1b727220a95u64.hash(&mut h1);
    0x9e3779b97f4a7c15u64.hash(&mut h2);

    verts.len().hash(&mut h1);
    faces.len().hash(&mut h1);
    verts.len().hash(&mut h2);
    faces.len().hash(&mut h2);

    sample_slice(verts, MAX_FINGERPRINT_SAMPLES, |v| {
        let bits = [v.x.to_bits(), v.y.to_bits(), v.z.to_bits()];
        bits.hash(&mut h1);
        [bits[2], bits[1], bits[0]].hash(&mut h2);
    });

    sample_slice(faces, MAX_FINGERPRINT_SAMPLES, |f| {
        f.hash(&mut h1);
        [f[2], f[1], f[0]].hash(&mut h2);
    });

    (h1.finish(), h2.finish())
}

pub fn get_or_build_trimesh(
    verts: &[Vector3<f64>],
    faces: &[[usize; 3]],
) -> PyResult<Arc<magba::base::mesh::TriMesh<f64>>> {
    let fingerprint = compute_mesh_fingerprint(verts, faces);

    if let Ok(mut guard) = MESH_CACHE.lock() {
        let mut match_idx = None;
        for (i, entry) in guard.entries.iter().enumerate() {
            if entry.fingerprint == fingerprint
                && entry.num_verts == verts.len()
                && entry.num_faces == faces.len()
            {
                match_idx = Some(i);
                break;
            }
        }
        if let Some(i) = match_idx {
            let entry = guard.entries.remove(i);
            let trimesh = Arc::clone(&entry.trimesh);
            guard.entries.insert(0, entry);
            return Ok(trimesh);
        }
    }

    let trimesh = magba::base::mesh::TriMesh::new(verts.iter().copied(), faces.iter().copied())
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("{:?}", e)))?;
    let trimesh_arc = Arc::new(trimesh);

    if faces.len() <= MAX_SINGLE_MESH_FACES {
        if let Ok(mut guard) = MESH_CACHE.lock() {
            while !guard.entries.is_empty()
                && (guard.entries.len() >= MAX_CACHE_ENTRIES
                    || guard.total_faces() + faces.len() > MAX_TOTAL_FACES)
            {
                guard.entries.pop();
            }
            guard.entries.insert(
                0,
                MeshCacheEntry {
                    fingerprint,
                    num_verts: verts.len(),
                    num_faces: faces.len(),
                    trimesh: Arc::clone(&trimesh_arc),
                },
            );
        }
    }

    Ok(trimesh_arc)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn valid_tetrahedron(offset: f64) -> (Vec<Vector3<f64>>, Vec<[usize; 3]>) {
        let verts = vec![
            Vector3::new(offset, 0.0, 0.0),
            Vector3::new(offset + 1.0, 0.0, 0.0),
            Vector3::new(offset, 1.0, 0.0),
            Vector3::new(offset, 0.0, 1.0),
        ];
        let faces = vec![[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]];
        (verts, faces)
    }

    #[test]
    fn test_fingerprint_sensitivity() {
        let (v1, f1) = valid_tetrahedron(0.0);
        let (v2, f2) = valid_tetrahedron(0.1);
        let fp1 = compute_mesh_fingerprint(&v1, &f1);
        let fp2 = compute_mesh_fingerprint(&v2, &f2);
        assert_ne!(fp1, fp2);
        assert_eq!(fp1, compute_mesh_fingerprint(&v1, &f1));
    }

    #[test]
    fn test_sample_slice() {
        let mut sampled = Vec::new();
        let items: Vec<usize> = (0..10).collect();
        sample_slice(&items, 64, |&x| sampled.push(x));
        assert_eq!(sampled, items);

        sampled.clear();
        let items_large: Vec<usize> = (0..1000).collect();
        sample_slice(&items_large, 10, |&x| sampled.push(x));
        assert_eq!(sampled.len(), 11); // 10 step samples + 1 end sample
        assert_eq!(sampled[0], 0);
        assert_eq!(*sampled.last().unwrap(), 999);
    }

    #[test]
    fn test_cache_hit_returns_same_arc() {
        let (v, f) = valid_tetrahedron(5.0);
        let arc1 = get_or_build_trimesh(&v, &f).expect("failed to build trimesh");
        let arc2 = get_or_build_trimesh(&v, &f).expect("failed to hit cache");
        assert!(Arc::ptr_eq(&arc1, &arc2));
    }
}
