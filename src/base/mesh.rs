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

struct MeshCacheEntry {
    hash: u64,
    num_verts: usize,
    num_faces: usize,
    verts: Vec<Vector3<f64>>,
    faces: Vec<[usize; 3]>,
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

pub fn get_or_build_trimesh(
    verts: Vec<Vector3<f64>>,
    faces: Vec<[usize; 3]>,
) -> PyResult<Arc<magba::base::mesh::TriMesh<f64>>> {
    use std::hash::{Hash, Hasher};

    let mut hasher = std::collections::hash_map::DefaultHasher::new();
    verts.len().hash(&mut hasher);
    faces.len().hash(&mut hasher);
    if !verts.is_empty() {
        let first = verts[0].as_slice();
        let mid = verts[verts.len() / 2].as_slice();
        let last = verts[verts.len() - 1].as_slice();
        for &v in first.iter().chain(mid).chain(last) {
            v.to_bits().hash(&mut hasher);
        }
    }
    if !faces.is_empty() {
        faces[0].hash(&mut hasher);
        faces[faces.len() / 2].hash(&mut hasher);
        faces[faces.len() - 1].hash(&mut hasher);
    }
    let h = hasher.finish();

    if let Ok(mut guard) = MESH_CACHE.lock() {
        let mut match_idx = None;
        for (i, entry) in guard.entries.iter().enumerate() {
            if entry.hash == h
                && entry.num_verts == verts.len()
                && entry.num_faces == faces.len()
                && entry.verts == verts
                && entry.faces == faces
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

    let trimesh = magba::base::mesh::TriMesh::new(verts.clone(), faces.clone())
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
                    hash: h,
                    num_verts: verts.len(),
                    num_faces: faces.len(),
                    verts,
                    faces,
                    trimesh: Arc::clone(&trimesh_arc),
                },
            );
        }
    }

    Ok(trimesh_arc)
}
