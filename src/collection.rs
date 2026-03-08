use pyo3::exceptions::PyIndexError;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};
use pyo3::IntoPyObject;
use std::sync::Arc;

use crate::{impl_compute_B, impl_pypose, magnets::*};

#[pyclass(subclass, from_py_object)]
#[derive(Clone)]
pub struct SourceCollection {
    pub(crate) inner: SourceAssembly<f64>,
    pub(crate) sources: Arc<Vec<Py<PyAny>>>,
}

use magba::collections::{ObserverAssembly, ObserverComponent, SourceAssembly, SourceComponent};

// SourceCollection does not implement Clone manually because Py<PyAny>
// cloning usually requires a Python token or GIL, and PyO3 handles
// class instance references.

#[pymethods]
impl SourceCollection {
    #[new]
    #[pyo3(signature = (sources=None))]
    fn new(sources: Option<Vec<Py<PyAny>>>, py: Python<'_>) -> PyResult<Self> {
        let mut components: Vec<SourceComponent<f64>> = Vec::new();
        let srcs = sources.unwrap_or_default();

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

        Ok(Self {
            inner: SourceAssembly::from(components),
            sources: Arc::new(srcs),
        })
    }

    fn __len__(&self) -> usize {
        self.sources.len()
    }

    fn __getitem__(&self, idx: isize, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let len = self.sources.len() as isize;
        let idx = if idx < 0 { len + idx } else { idx };
        if idx < 0 || idx >= len {
            return Err(PyIndexError::new_err("index out of range"));
        }
        Ok(self.sources[idx as usize].clone_ref(py))
    }

    fn append(&mut self, source: Py<PyAny>, py: Python<'_>) -> PyResult<()> {
        let bound = source.bind(py);
        if let Ok(m) = bound.extract::<PyRef<'_, CylinderMagnet>>() {
            self.inner.push(m.inner.clone());
        } else if let Ok(m) = bound.extract::<PyRef<'_, CuboidMagnet>>() {
            self.inner.push(m.inner.clone());
        } else if let Ok(m) = bound.extract::<PyRef<'_, Dipole>>() {
            self.inner.push(m.inner.clone());
        } else if let Ok(m) = bound.extract::<PyRef<'_, SourceCollection>>() {
            self.inner.push(m.inner.clone());
        } else {
            return Err(pyo3::exceptions::PyTypeError::new_err(
                "source must be CylinderMagnet, CuboidMagnet, Dipole, or SourceCollection",
            ));
        }

        let mut new_sources: Vec<Py<PyAny>> =
            self.sources.iter().map(|s| s.clone_ref(py)).collect();
        new_sources.push(source);
        self.sources = Arc::new(new_sources);
        Ok(())
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new(py);
        dict.set_item("sources", self.sources.as_ref())?;
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, PyDict>, py: Python<'_>) -> PyResult<()> {
        let sources_bound = state
            .get_item("sources")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("sources missing from state"))?;
        let sources: Vec<Py<PyAny>> = sources_bound.extract()?;

        let pos_bound = state
            .get_item("position")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("position missing from state"))?;
        let position: [f64; 3] = pos_bound.extract()?;

        let rot_bound = state.get_item("orientation")?.ok_or_else(|| {
            pyo3::exceptions::PyKeyError::new_err("orientation missing from state")
        })?;
        let orientation: [f64; 4] = rot_bound.extract()?;

        let mut components: Vec<SourceComponent<f64>> = Vec::new();
        for src in sources.iter() {
            let bound = src.bind(py);
            if let Ok(m) = bound.extract::<PyRef<'_, CylinderMagnet>>() {
                components.push(m.inner.clone().into());
            } else if let Ok(m) = bound.extract::<PyRef<'_, CuboidMagnet>>() {
                components.push(m.inner.clone().into());
            } else if let Ok(m) = bound.extract::<PyRef<'_, Dipole>>() {
                components.push(m.inner.clone().into());
            } else if let Ok(m) = bound.extract::<PyRef<'_, SourceCollection>>() {
                components.push(m.inner.clone().into());
            }
        }

        let mut inner = SourceAssembly::from(components);
        inner.set_position(position);
        inner.set_orientation(nalgebra::UnitQuaternion::from_quaternion(
            nalgebra::Quaternion::from_vector(orientation.into()),
        ));

        self.inner = inner;
        self.sources = Arc::new(sources);
        Ok(())
    }

    fn __reduce__<'py>(slf: Bound<'py, Self>, py: Python<'py>) -> PyResult<Bound<'py, PyTuple>> {
        let cls = slf.get_type();
        let borrow = slf.borrow();
        let sources_list = PyList::new(py, borrow.sources.as_ref())?;
        let args = PyTuple::new(py, [sources_list.into_any()])?;
        let state = borrow.__getstate__(py)?;
        PyTuple::new(
            py,
            [
                cls.into_any(),
                args.into_any(),
                state.into_bound(py).into_any(),
            ],
        )
    }
}

impl_pypose!(SourceCollection);
impl_compute_B!(SourceCollection);

#[pyclass(subclass, from_py_object)]
#[derive(Clone)]
pub struct ObserverCollection {
    pub(crate) inner: ObserverAssembly<f64>,
    pub(crate) sensors: Arc<Vec<Py<PyAny>>>,
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
        let sens = sensors.unwrap_or_default();

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

        let pos: nalgebra::Point3<f64> = position
            .map(|p| p.0.into())
            .unwrap_or_else(|| [0.0, 0.0, 0.0].into());
        let rot: nalgebra::UnitQuaternion<f64> = orientation
            .map(|rot| rot.0)
            .unwrap_or_else(nalgebra::UnitQuaternion::identity);

        let mut inner = ObserverAssembly::from(components);
        inner.set_position(pos);
        inner.set_orientation(rot);

        Ok(Self {
            inner,
            sensors: Arc::new(sens),
        })
    }

    fn __len__(&self) -> usize {
        self.sensors.len()
    }

    fn __getitem__(&self, idx: isize, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let len = self.sensors.len() as isize;
        let idx = if idx < 0 { len + idx } else { idx };
        if idx < 0 || idx >= len {
            return Err(PyIndexError::new_err("index out of range"));
        }
        Ok(self.sensors[idx as usize].clone_ref(py))
    }

    fn append(&mut self, sensor: Py<PyAny>, py: Python<'_>) -> PyResult<()> {
        let bound = sensor.bind(py);
        if let Ok(s) = bound.extract::<PyRef<'_, crate::sensors::LinearHallSensor>>() {
            self.inner.push(s.inner.clone());
        } else if let Ok(s) = bound.extract::<PyRef<'_, crate::sensors::HallSwitch>>() {
            self.inner.push(s.inner.clone());
        } else if let Ok(s) = bound.extract::<PyRef<'_, crate::sensors::HallLatch>>() {
            self.inner.push(s.inner.clone());
        } else {
            return Err(pyo3::exceptions::PyTypeError::new_err(
                "sensor must be LinearHallSensor, HallSwitch, or HallLatch",
            ));
        }

        let mut new_sensors: Vec<Py<PyAny>> =
            self.sensors.iter().map(|s| s.clone_ref(py)).collect();
        new_sensors.push(sensor);
        self.sensors = Arc::new(new_sensors);
        Ok(())
    }

    fn __getstate__(&self, py: Python<'_>) -> PyResult<Py<PyDict>> {
        let dict = PyDict::new(py);
        dict.set_item("sensors", self.sensors.as_ref())?;
        dict.set_item("position", <[f64; 3]>::from(self.inner.position().coords))?;
        dict.set_item(
            "orientation",
            <[f64; 4]>::from(self.inner.orientation().into_inner().coords),
        )?;
        Ok(dict.unbind())
    }

    fn __setstate__(&mut self, state: Bound<'_, PyDict>, py: Python<'_>) -> PyResult<()> {
        let sensors_bound = state
            .get_item("sensors")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("sensors missing from state"))?;
        let sensors: Vec<Py<PyAny>> = sensors_bound.extract()?;

        let pos_bound = state
            .get_item("position")?
            .ok_or_else(|| pyo3::exceptions::PyKeyError::new_err("position missing from state"))?;
        let position: [f64; 3] = pos_bound.extract()?;

        let rot_bound = state.get_item("orientation")?.ok_or_else(|| {
            pyo3::exceptions::PyKeyError::new_err("orientation missing from state")
        })?;
        let orientation: [f64; 4] = rot_bound.extract()?;

        let mut components: Vec<ObserverComponent<f64>> = Vec::new();
        for s in &sensors {
            let bound = s.bind(py);
            if let Ok(s) = bound.extract::<PyRef<'_, crate::sensors::LinearHallSensor>>() {
                components.push(s.inner.clone().into());
            } else if let Ok(s) = bound.extract::<PyRef<'_, crate::sensors::HallSwitch>>() {
                components.push(s.inner.clone().into());
            } else if let Ok(s) = bound.extract::<PyRef<'_, crate::sensors::HallLatch>>() {
                components.push(s.inner.clone().into());
            }
        }

        let mut inner = ObserverAssembly::from(components);
        inner.set_position(nalgebra::Point3::from(position));
        inner.set_orientation(nalgebra::UnitQuaternion::from_quaternion(
            nalgebra::Quaternion::from_vector(orientation.into()),
        ));

        self.inner = inner;
        self.sensors = Arc::new(sensors);
        Ok(())
    }

    fn __reduce__<'py>(slf: Bound<'py, Self>, py: Python<'py>) -> PyResult<Bound<'py, PyTuple>> {
        let cls = slf.get_type();
        let borrow = slf.borrow();
        let sensors_list = PyList::new(py, borrow.sensors.as_ref())?;
        let args = PyTuple::new(py, [sensors_list.into_any()])?;
        let state = borrow.__getstate__(py)?;
        PyTuple::new(
            py,
            [
                cls.into_any(),
                args.into_any(),
                state.into_bound(py).into_any(),
            ],
        )
    }

    fn read_all(&self, source: Bound<'_, PyAny>, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let results = if let Ok(m) = source.extract::<PyRef<'_, CylinderMagnet>>() {
            self.inner.read_all(&m.inner)
        } else if let Ok(m) = source.extract::<PyRef<'_, CuboidMagnet>>() {
            self.inner.read_all(&m.inner)
        } else if let Ok(m) = source.extract::<PyRef<'_, Dipole>>() {
            self.inner.read_all(&m.inner)
        } else if let Ok(m) = source.extract::<PyRef<'_, SourceCollection>>() {
            self.inner.read_all(&m.inner)
        } else {
            return Err(pyo3::exceptions::PyTypeError::new_err(
                "source must be CylinderMagnet, CuboidMagnet, Dipole, or SourceCollection",
            ));
        };

        let list = PyList::empty(py);
        for o in results {
            list.append(sensor_output_to_py(py, o))?;
        }
        Ok(list.into_any().unbind())
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
