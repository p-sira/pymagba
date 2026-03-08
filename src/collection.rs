use magba::collections::{ObserverAssembly, ObserverComponent, SourceAssembly, SourceComponent};
use pyo3::prelude::*;
use pyo3::types::PyList;
use pyo3::IntoPyObject;

use crate::{impl_compute_B, impl_pypose, magnets::*};

#[pyclass(subclass, from_py_object)]
#[derive(Clone)]
pub struct SourceCollection {
    pub(crate) inner: SourceAssembly<f64>,
}

#[pymethods]
impl SourceCollection {
    #[new]
    #[pyo3(signature = (sources=None))]
    fn new(sources: Option<Vec<Py<PyAny>>>, py: Python<'_>) -> PyResult<Self> {
        let mut components: Vec<SourceComponent<f64>> = Vec::new();

        if let Some(srcs) = sources {
            for src in &srcs {
                if let Ok(m) = src.extract::<PyRef<'_, CylinderMagnet>>(py) {
                    components.push(m.inner.clone().into());
                } else if let Ok(m) = src.extract::<PyRef<'_, CuboidMagnet>>(py) {
                    components.push(m.inner.clone().into());
                } else if let Ok(m) = src.extract::<PyRef<'_, Dipole>>(py) {
                    components.push(m.inner.clone().into());
                } else {
                    return Err(pyo3::exceptions::PyTypeError::new_err(
                        "sources must be CylinderMagnet, CuboidMagnet, or Dipole",
                    ));
                }
            }
        }

        Ok(Self {
            inner: SourceAssembly::from(components),
        })
    }
}

impl_pypose!(SourceCollection);
impl_compute_B!(SourceCollection);

#[pyclass(subclass, from_py_object)]
#[derive(Clone)]
pub struct ObserverCollection {
    pub(crate) inner: ObserverAssembly<f64>,
}

#[pymethods]
impl ObserverCollection {
    #[new]
    #[pyo3(signature = (sensors=None, position=None, orientation=None))]
    fn new(
        sensors: Option<Vec<Py<PyAny>>>,
        position: Option<crate::util::ArrayLike3>,
        orientation: Option<crate::util::PyRotation>,
        py: Python<'_>,
    ) -> PyResult<Self> {
        let mut components: Vec<ObserverComponent<f64>> = Vec::new();

        if let Some(sens) = sensors {
            for s in &sens {
                if let Ok(s) = s.extract::<PyRef<'_, crate::sensors::LinearHallSensor>>(py) {
                    components.push(s.inner.clone().into());
                } else if let Ok(s) = s.extract::<PyRef<'_, crate::sensors::HallSwitch>>(py) {
                    components.push(s.inner.clone().into());
                } else if let Ok(s) = s.extract::<PyRef<'_, crate::sensors::HallLatch>>(py) {
                    components.push(s.inner.clone().into());
                } else {
                    return Err(pyo3::exceptions::PyTypeError::new_err(
                        "sensors must be LinearHallSensor, HallSwitch, or HallLatch",
                    ));
                }
            }
        }

        let pos: nalgebra::Point3<f64> = position
            .map(|p| p.0.into())
            .unwrap_or_else(|| [0.0, 0.0, 0.0].into());
        let rot: nalgebra::UnitQuaternion<f64> = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);

        let mut inner = ObserverAssembly::from(components);
        inner.set_position(pos);
        inner.set_orientation(rot);

        Ok(Self { inner })
    }

    fn read_all_cylinder(&self, source: &CylinderMagnet, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let results = self.inner.read_all(&source.inner);
        let list = PyList::empty(py);
        for o in results {
            list.append(sensor_output_to_py(py, o))?;
        }
        Ok(list.into_any().unbind())
    }

    fn read_all_cuboid(&self, source: &CuboidMagnet, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let results = self.inner.read_all(&source.inner);
        let list = PyList::empty(py);
        for o in results {
            list.append(sensor_output_to_py(py, o))?;
        }
        Ok(list.into_any().unbind())
    }

    fn read_all_dipole(&self, source: &Dipole, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let results = self.inner.read_all(&source.inner);
        let list = PyList::empty(py);
        for o in results {
            list.append(sensor_output_to_py(py, o))?;
        }
        Ok(list.into_any().unbind())
    }

    fn read_all_collection(
        &self,
        source: &SourceCollection,
        py: Python<'_>,
    ) -> PyResult<Py<PyAny>> {
        let results = self.inner.read_all(&source.inner);
        let list = PyList::empty(py);
        for o in results {
            list.append(sensor_output_to_py(py, o))?;
        }
        Ok(list.into_any().unbind())
    }

    fn read_all(&self, source: Bound<'_, PyAny>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        if let Ok(m) = source.extract::<PyRef<'_, CylinderMagnet>>() {
            self.read_all_cylinder(&m, py)
        } else if let Ok(m) = source.extract::<PyRef<'_, CuboidMagnet>>() {
            self.read_all_cuboid(&m, py)
        } else if let Ok(m) = source.extract::<PyRef<'_, Dipole>>() {
            self.read_all_dipole(&m, py)
        } else if let Ok(m) = source.extract::<PyRef<'_, SourceCollection>>() {
            self.read_all_collection(&m, py)
        } else {
            Err(pyo3::exceptions::PyTypeError::new_err(
                "source must be CylinderMagnet, CuboidMagnet, Dipole, or SourceCollection",
            ))
        }
    }
}

impl_pypose!(ObserverCollection);

fn sensor_output_to_py(py: Python<'_>, output: magba::base::SensorOutput<f64>) -> Py<PyAny> {
    match output {
        magba::base::SensorOutput::Scalar(val) => {
            val.into_pyobject(py).unwrap().into_any().unbind()
        }
        magba::base::SensorOutput::Vector(vec) => {
            let np = py.import("numpy").unwrap();
            let arr = np.call_method1("array", ([vec.x, vec.y, vec.z],)).unwrap();
            arr.into_any().unbind()
        }
        magba::base::SensorOutput::Digital(val) => {
            val.into_pyobject(py).unwrap().into_any().unbind()
        }
    }
}
