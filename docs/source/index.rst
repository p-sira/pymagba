.. pymagba documentation master file, created by
   sphinx-quickstart on Fri Mar  6 21:14:01 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyMagba Documentation
=====================

.. raw:: html

   <h1 align="center">
      <a href="https://github.com/p-sira/pymagba/">
         <img src="_static/pymagba-logo-fit.svg" alt="PyMagba" width="350" style="background-color: transparent;">
      </a>
   </h1>

   <p align="center">
      <a href="https://opensource.org/license/BSD-3-clause">
         <img src="https://img.shields.io/badge/License-BSD--3--Clause-brightgreen.svg" alt="License">
      </a>
      <a href="https://pypi.org/project/pymagba">
         <img src="https://img.shields.io/pypi/v/pymagba?label=pypi%20package" alt="PyPI Package">
      </a>
      <a href="https://pypi.org/project/pymagba">
         <img src="https://static.pepy.tech/personalized-badge/pymagba?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=BRIGHTGREEN&left_text=downloads" alt="Total Downloads">
      </a>
      <a href="https://p-sira.github.io/pymagba">
         <img src="https://img.shields.io/badge/Docs-github.io-blue" alt="Documentation">
      </a>
   </p>

----

**PyMagba** is a package for analytical magnetic computation, powered by Rust. All functions support numpy and parallelization.

Quick Start
-----------

.. code:: python

   from pymagba.magnets import *
   from pymagba.sensors import *

   magnet = CylinderMagnet(
      position=[0.0, 0.0, 0.01],
      diameter=0.01,
      height=0.005,
      polarization=[0.0, 0.0, 1.0],
   )
   sensor = LinearHallSensor(
      position=[0.0, 0.0, 0.025],
      sensitive_axis=[0.0, 0.0, 1.0],
      sensitivity=0.05,
      supply_voltage=5.0,
   )
   b_field = magnet.compute_B([0.0, 0.0, 0.025])  # [[0, 0, 0.01652363]]
   voltage = sensor.read_voltage_cylinder(magnet)  # 2.5008261


To install PyMagba, use your preferred package manager:

.. code:: shell
   
   pip install pymagba

.. code:: shell
   
   uv add pymagba

To install from source:

.. code:: shell
   
   git clone https://github.com/p-sira/pymagba.git
   cd pymagba
   maturin build --release
   pip install target/wheels/pymagba-*.whl

.. toctree::
   :maxdepth: 2
   :caption: Submodules

   magnets
   sensors
