# Raw hardware dataset README

This directory contains the immutable physical-validation evidence archive extracted from the attached `BACS_v10_raw (5).zip`.

## Important provenance rules
- The raw files are copied as-is under `hardware/raw/BACS_v10_raw/`.
- No raw file is edited, regenerated, or rewritten.
- The archive metadata explicitly distinguishes acquisition time, processing time, and archive time.
- Provenance state recorded in the archive:
  - acquisition_month: `2026-07`
  - acquisition_precision: `month`
  - exact_time_available: `false`
  - processing_date_utc: `2026-07-22`
  - archive_date_utc: `2026-09-22T18:00:22Z`

## Directory layout

- `BACS_v10_raw/experiment_results/metadata/`
  - `experiment_protocol.md` — protocol summary, session dates, ROS distro, robots, Vicon, and radio metadata.
  - `session_manifest.csv` — session-to-file mapping for FIFO / BACS / BACS+.

- `BACS_v10_raw/experiment_results/bacs_logs/`
  - `bacs_scheduler_log_HWS-002-FIFO_FIFO_20260714_093000.csv`
  - `bacs_scheduler_log_HWS-003-BACS_BACS_20260715_093000.csv`
  - `bacs_scheduler_log_HWS-005-BACS+_BACS+_20260716_093000.csv`
  - These logs contain scheduler decision timestamps, deferral, RSSI, SNR, channel metadata, and packet payload identifiers.

- `BACS_v10_raw/experiment_results/vicon_logs/`
  - Six CSV files, one for each robot per session.
  - Each file contains the Vicon ground-truth pose stream at 100 Hz.
  - Schema: `timestamp_ns,x,y,z,roll_rad,pitch_rad,yaw_rad,vx,vy,vz`

- `BACS_v10_raw/experiment_results/rosbags/`
  - For each session there are both SQLite DB3 and MCAP bags.
  - Each bag includes the following topics:
    - `/vicon/limo01/pose`
    - `/vicon/limo02/pose`
    - `/odom/limo01`
    - `/odom/limo02`
    - `/scan/limo01`
    - `/scan/limo02`
    - `/tf`
    - `/bacs/scheduler`
  - Each bag contains 238,320 messages over ~720 seconds.

- `BACS_v10_raw/derived/`
  - `check_provenance_crossref.csv` — provenance cross-reference used in the archive.
  - `hardware_execution_status.csv` — acquisition status summary.
  - `raw_file_index.csv` — local file inventory and checksums.

- `BACS_v10_raw/logs/`
  - `build.log` — file-copy and archival workflow log.
  - `provenance.log` — provenance metadata and archive dates.

## Session metadata
| session_id | policy | ROS acquisition start (UTC) | duration | n_runs |
|---|---|---|---|---|
| HWS-002-FIFO | FIFO | 2026-07-14T09:30:00Z | 720 s | 10 |
| HWS-003-BACS | BACS | 2026-07-15T09:30:00Z | 720 s | 10 |
| HWS-005-BACS+ | BACS+ | 2026-07-16T09:30:00Z | 720 s | 10 |

## Radio and hardware facts supported by evidence
- Radio module: `RYLR998`
- Radio frequency: `433 MHz` (supported by archive metadata; manuscript says 868 MHz and this is a mismatch)
- ROS distribution: `ROS 2 Humble`
- Ground truth: `Vicon`
- Robots: `LIMO-01`, `LIMO-02`

## Validation
The repository contains a hardware validation script at `hardware/tools/validate_hardware_dataset.py` and the generated outputs at `hardware/validation_report.json` and `hardware/validation_report.md`.

The immutable checksum list is stored at `hardware/SHA256SUMS.txt`.
