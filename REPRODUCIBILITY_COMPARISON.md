# Reproducibility comparison

The publication repository combines the evidence-preserving physical archive from
this repository with the simulation and ROS 2 implementation from
[`MagyElbanhawy/ros2_BACS`](https://github.com/MagyElbanhawy/ros2_BACS).

## Imported publication surfaces

- `bacs_sim/`: simulator, scheduler policies, trust, observability, pose graph,
  and experiment runners.
- `ros2_ws/src/bacs_scheduler/`: ROS 2 BACS/BACS+ package, custom messages,
  configuration, launch files, and physical-session scripts.
- `paper_results/`: frozen progression, S7-C, S8, S9, and hardware-status tables.
- `paper_figures/`: frozen publication figures.
- `scripts/`: baseline reproduction, S8 30-seed runner, figure generation,
  integration checks, and physical batch/analysis utilities.
- `tests/`: simulator and BACS+ regression tests.

## Evidence boundary

The imported source repository contains the simulation runners and frozen outputs
needed to reproduce S7-C, S8, and S9 computationally. It does not supply a
per-run physical map-alignment result file or a serialized map/pose-estimate
stream sufficient to recompute physical Table 6.

The raw physical archive does contain:

- ten scheduler run labels (`1` through `10`) for each FIFO, BACS, and BACS+
  session;
- Vicon ground-truth CSVs for both robots;
- scheduler timing, RSSI, SNR, and payload fields;
- DB3/MCAP bag metadata and raw bag files.

It does not contain the derived per-run map-alignment RMSE values required to
independently obtain the paper's physical targets:

| Policy | Paper target | Current repository status |
|---|---:|---|
| FIFO | `0.48 +/- 0.15 m` | Target documented; not recomputable from supplied raw streams |
| BACS | `0.28 +/- 0.08 m` | Target documented; not recomputable from supplied raw streams |
| BACS+ | `0.27 +/- 0.09 m` | Target documented; not recomputable from supplied raw streams |

The paper also reports median scheduling deferral of `154 s`, median channel
delay of `0.17 s`, and a `906x` ratio. The audit script records those as paper
targets, but does not claim to reproduce them: the current scheduler logs have
timing fields, yet their observed scales do not independently recover those
headline values.

Run:

```bash
python analysis/physical/table6_physical.py
```

The command writes a machine-readable report under
`paper_results/physical_table6_audit.json` and a CSV of available
communication diagnostics. It never fabricates the missing RMSE values.
