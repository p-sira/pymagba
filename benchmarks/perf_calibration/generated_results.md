# Extracted Calibration Thresholds

Reports:

- `benchmark-results/ffi-threshold-20261004-114138-158316/report.json`

## Conservative Rayon Recommendations

The recommendation is the largest stable crossover among the
functional/object variants present in the supplied reports. Review
variable-complexity workloads before changing code. Source collections
remain in the detailed table but are excluded from this point-only summary.

| Case | First parallel size | Stored `len >` threshold | Candidate range | Workloads |
| --- | ---: | ---: | ---: | ---: |
| circular | 1,023 | 1,022 | 819-1,023 | 2 |
| cuboid | 127 | 126 | 127-127 | 2 |
| cylinder | 819 | 818 | 205-819 | 4 |
| dipole | 32,768 | 32,767 | 0-32,768 | 2 |
| mesh | 26 | 25 | 11-26 | 4 |
| path | 410 | 409 | 45-410 | 4 |
| sheet | 26 | 25 | 16-26 | 4 |
| sphere | 39,322 | 39,321 | 36,045-39,322 | 2 |
| tetrahedron | 127 | 126 | 127-127 | 2 |
| triangle | 819 | 818 | 511-819 | 2 |
| triangle_current | 410 | 409 | 410-410 | 2 |

## Rayon Candidates

| Family | Case | Workload | Status | Candidate | Maximum tested | Limit |
| --- | --- | --- | --- | ---: | ---: | --- |
| field | circular | functional, complexity=1 | crossover | 819 | 65536 | — |
| field | circular | object, complexity=1 | crossover | 1023 | 65536 | — |
| field | collection | object, variant=homogeneous, complexity=32 | crossover | 511 | 1024 | — |
| field | collection | object, variant=homogeneous, complexity=4 | crossover | 8191 | 65536 | — |
| field | collection | object, variant=mixed, complexity=32 | crossover | 13 | 1024 | — |
| field | collection | object, variant=mixed, complexity=4 | crossover | 102 | 1024 | — |
| field | collection | object, variant=nested, complexity=32 | crossover | 13 | 1024 | — |
| field | collection | object, variant=nested, complexity=4 | crossover | 127 | 1024 | — |
| field | cuboid | functional, complexity=1 | crossover | 127 | 1024 | — |
| field | cuboid | object, complexity=1 | crossover | 127 | 1024 | — |
| field | cylinder | functional, variant=axial, complexity=1 | crossover | 819 | 65536 | — |
| field | cylinder | functional, variant=mixed, complexity=1 | crossover | 205 | 1024 | — |
| field | cylinder | object, variant=axial, complexity=1 | crossover | 511 | 1024 | — |
| field | cylinder | object, variant=mixed, complexity=1 | crossover | 205 | 1024 | — |
| field | dipole | functional, complexity=1 | crossover | 0 | 1024 | — |
| field | dipole | object, complexity=1 | crossover | 32768 | 65536 | — |
| field | mesh | functional, complexity=32 | crossover | 11 | 1024 | — |
| field | mesh | functional, complexity=4 | crossover | 26 | 1024 | — |
| field | mesh | object, complexity=32 | crossover | 13 | 1024 | — |
| field | mesh | object, complexity=4 | crossover | 26 | 1024 | — |
| field | path | functional, complexity=32 | crossover | 51 | 1024 | — |
| field | path | functional, complexity=4 | crossover | 410 | 1024 | — |
| field | path | object, complexity=32 | crossover | 45 | 1024 | — |
| field | path | object, complexity=4 | crossover | 410 | 1024 | — |
| field | sheet | functional, complexity=32 | crossover | 16 | 1024 | — |
| field | sheet | functional, complexity=4 | crossover | 26 | 1024 | — |
| field | sheet | object, complexity=32 | crossover | 16 | 1024 | — |
| field | sheet | object, complexity=4 | crossover | 26 | 1024 | — |
| field | sphere | functional, complexity=1 | crossover | 39322 | 65537 | — |
| field | sphere | object, complexity=1 | crossover | 36045 | 65536 | — |
| field | tetrahedron | functional, complexity=1 | crossover | 127 | 1024 | — |
| field | tetrahedron | object, complexity=1 | crossover | 127 | 1024 | — |
| field | triangle | functional, complexity=1 | crossover | 819 | 65536 | — |
| field | triangle | object, complexity=1 | crossover | 511 | 1024 | — |
| field | triangle_current | functional, complexity=1 | crossover | 410 | 1024 | — |
| field | triangle_current | object, complexity=1 | crossover | 410 | 1024 | — |

## GIL Candidates

| Family | Case | Workload | Status | Candidate | Maximum tested | Limit |
| --- | --- | --- | --- | ---: | ---: | --- |
| field | circular | functional, complexity=1 | no_crossover | — | 65536 | max_work_size |
| field | circular | object, complexity=1 | inconclusive | — | 1024 | extension_steps |
| field | collection | object, variant=homogeneous, complexity=32 | inconclusive | — | 65536 | max_work_size |
| field | collection | object, variant=homogeneous, complexity=4 | crossover | 64 | 1024 | — |
| field | collection | object, variant=mixed, complexity=32 | crossover | 32 | 1024 | — |
| field | collection | object, variant=mixed, complexity=4 | inconclusive | — | 65536 | max_work_size |
| field | collection | object, variant=nested, complexity=32 | crossover | 1 | 1024 | — |
| field | collection | object, variant=nested, complexity=4 | crossover | 16 | 1024 | — |
| field | cuboid | functional, complexity=1 | no_crossover | — | 65536 | max_work_size |
| field | cuboid | object, complexity=1 | no_crossover | — | 65536 | max_work_size |
| field | cylinder | functional, variant=axial, complexity=1 | no_crossover | — | 65536 | max_work_size |
| field | cylinder | functional, variant=mixed, complexity=1 | no_crossover | — | 65536 | max_work_size |
| field | cylinder | object, variant=axial, complexity=1 | inconclusive | — | 65536 | max_work_size |
| field | cylinder | object, variant=mixed, complexity=1 | crossover | 8192 | 65536 | — |
| field | dipole | functional, complexity=1 | inconclusive | — | 65536 | max_work_size |
| field | dipole | object, complexity=1 | inconclusive | — | 65536 | max_work_size |
| field | mesh | functional, complexity=32 | inconclusive | — | 65536 | max_work_size |
| field | mesh | functional, complexity=4 | inconclusive | — | 65536 | max_work_size |
| field | mesh | object, complexity=32 | crossover | 64 | 1024 | — |
| field | mesh | object, complexity=4 | crossover | 64 | 1024 | — |
| field | path | functional, complexity=32 | inconclusive | — | 65536 | max_work_size |
| field | path | functional, complexity=4 | crossover | 0 | 1024 | — |
| field | path | object, complexity=32 | crossover | 255 | 1024 | — |
| field | path | object, complexity=4 | inconclusive | — | 65536 | max_work_size |
| field | sheet | functional, complexity=32 | no_crossover | — | 65536 | max_work_size |
| field | sheet | functional, complexity=4 | crossover | 128 | 1024 | — |
| field | sheet | object, complexity=32 | inconclusive | — | 65536 | max_work_size |
| field | sheet | object, complexity=4 | inconclusive | — | 65536 | max_work_size |
| field | sphere | functional, complexity=1 | no_crossover | — | 65536 | max_work_size |
| field | sphere | object, complexity=1 | no_crossover | — | 65536 | max_work_size |
| field | tetrahedron | functional, complexity=1 | inconclusive | — | 1024 | extension_steps |
| field | tetrahedron | object, complexity=1 | inconclusive | — | 65536 | max_work_size |
| field | triangle | functional, complexity=1 | no_crossover | — | 65536 | max_work_size |
| field | triangle | object, complexity=1 | crossover | 1023 | 65536 | — |
| field | triangle_current | functional, complexity=1 | crossover | 256 | 65536 | — |
| field | triangle_current | object, complexity=1 | crossover | 1 | 1024 | — |
| sensor | latch_read | sensor, source=collection | no_crossover | — | 2048 | extension_steps |
| sensor | latch_read | sensor, source=dipole | no_crossover | — | 64 | extension_steps |
| sensor | latch_read | sensor, source=path | no_crossover | — | 2048 | extension_steps |
| sensor | latch_read | sensor, source=sheet | no_crossover | — | 2048 | extension_steps |
| sensor | latch_state | sensor, source=collection | no_crossover | — | 2048 | extension_steps |
| sensor | latch_state | sensor, source=dipole | no_crossover | — | 64 | extension_steps |
| sensor | latch_state | sensor, source=path | no_crossover | — | 2048 | extension_steps |
| sensor | latch_state | sensor, source=sheet | no_crossover | — | 2048 | extension_steps |
| sensor | linear_perp | sensor, source=collection | no_crossover | — | 2048 | extension_steps |
| sensor | linear_perp | sensor, source=dipole | no_crossover | — | 64 | extension_steps |
| sensor | linear_perp | sensor, source=path | no_crossover | — | 2048 | extension_steps |
| sensor | linear_perp | sensor, source=sheet | no_crossover | — | 2048 | extension_steps |
| sensor | linear_read | sensor, source=collection | no_crossover | — | 2048 | extension_steps |
| sensor | linear_read | sensor, source=dipole | no_crossover | — | 64 | extension_steps |
| sensor | linear_read | sensor, source=path | inconclusive | — | 2048 | extension_steps |
| sensor | linear_read | sensor, source=sheet | no_crossover | — | 2048 | extension_steps |
| sensor | linear_voltage | sensor, source=collection | no_crossover | — | 2048 | extension_steps |
| sensor | linear_voltage | sensor, source=dipole | no_crossover | — | 64 | extension_steps |
| sensor | linear_voltage | sensor, source=path | inconclusive | — | 2049 | extension_steps |
| sensor | linear_voltage | sensor, source=sheet | no_crossover | — | 2048 | extension_steps |
| sensor | observer_mixed | sensor, source=collection, complexity=32 | no_crossover | — | 4096 | extension_steps |
| sensor | observer_mixed | sensor, source=collection, complexity=4 | no_crossover | — | 4096 | extension_steps |
| sensor | observer_mixed | sensor, source=dipole, complexity=1 | no_crossover | — | 4096 | extension_steps |
| sensor | observer_mixed | sensor, source=path, complexity=32 | no_crossover | — | 4096 | extension_steps |
| sensor | observer_mixed | sensor, source=path, complexity=4 | inconclusive | — | 4096 | extension_steps |
| sensor | observer_mixed | sensor, source=sheet, complexity=32 | inconclusive | — | 64 | extension_steps |
| sensor | observer_mixed | sensor, source=sheet, complexity=4 | no_crossover | — | 4096 | extension_steps |
| sensor | switch_read | sensor, source=collection | no_crossover | — | 2048 | extension_steps |
| sensor | switch_read | sensor, source=dipole | no_crossover | — | 64 | extension_steps |
| sensor | switch_read | sensor, source=path | no_crossover | — | 2048 | extension_steps |
| sensor | switch_read | sensor, source=sheet | no_crossover | — | 2048 | extension_steps |
| sensor | switch_state | sensor, source=collection | no_crossover | — | 2048 | extension_steps |
| sensor | switch_state | sensor, source=dipole | no_crossover | — | 64 | extension_steps |
| sensor | switch_state | sensor, source=path | no_crossover | — | 2048 | extension_steps |
| sensor | switch_state | sensor, source=sheet | no_crossover | — | 2048 | extension_steps |
