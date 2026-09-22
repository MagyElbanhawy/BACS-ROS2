# Audit Report: BACS v10 manuscript vs raw evidence

## Scope
This audit compares:
- the manuscript file `BACS_v10.docx`
- the raw hardware evidence archive `BACS_v10_raw (5).zip`
- the extracted raw evidence under `hardware/raw/BACS_v10_raw/`

The raw hardware archive is treated as the source of truth for physical-validation claims. The manuscript and earlier repository materials are reviewed only as secondary inputs.

## Raw-evidence summary
The archive contains three session folders with consistent metadata:
- `HWS-002-FIFO` — FIFO — 2026-07-14T09:30:00Z
- `HWS-003-BACS` — BACS — 2026-07-15T09:30:00Z
- `HWS-005-BACS+` — BACS+ — 2026-07-16T09:30:00Z

Per-session evidence includes:
- ROS 2 SQLite DB3 bag
- ROS 2 MCAP bag
- Vicon ground-truth CSV for both robots
- scheduler CSV for the policy run
- session manifest and metadata
- provenance CSVs and logs

The raw archive explicitly states:
- acquisition month: `2026-07`
- acquisition precision: `month`
- exact time available: `false`
- processing date: `2026-07-22`
- archive date: `2026-09-22T18:00:22Z`

These values must be distinguished from ROS-recorded timestamps and file timestamps.

## Key discrepancies and mismatches
1. The manuscript states the radio is `RYLR998 LoRa` at `868 MHz`.
   - The raw hardware metadata and logs say `RYLR998` and `433 MHz`.
   - This is a direct mismatch and is reported as such.

2. The manuscript states the physical hardware system as modified AgileX LIMO robots with Ubuntu 22.04, Intel NUC i7, EAI T-mini Pro LiDAR, Orbbec DaBai RGB-D, and a 1% duty-cycle condition.
   - The raw data supports ROS 2 Humble, Vicon, ROS bags, scheduler logs, and `LIMO-01/LIMO-02` by name.
   - It does not provide independent evidence for Ubuntu 22.04, Intel NUC i7, EAI T-mini Pro, Orbbec DaBai, or the exact 1% duty-cycle setting across the sessions.

3. The manuscript describes a 60 s scheduling window.
   - The raw data does not contain a file or metadata field that records `W = 60 s` as an experiment parameter.
   - The scheduler logs show per-message deferral and channel times, but not an explicit 60 s window declaration.

4. The manuscript mentions `10 matched runs per policy`.
   - The archive metadata declares `n_runs = 10` in `session_manifest.csv` and the derived provenance files.
   - Each policy scheduler log independently contains run labels `1` through `10`, so the ten-run count is supported by both metadata and raw scheduler records. This does not imply that the missing Table 6 RMSE values can be reconstructed.

5. The manuscript claims `session duration` and lines about 720 s / 12 minutes are consistent with the raw data and the ROS bag metadata.

6. The raw archive contains the real acquisition timestamps for each session as ROS timestamps and is consistent with session names and dates.
   - The archive does not provide a verified wall-clock log for the whole physical laboratory setup beyond month-level provenance metadata.

## Classification matrix

| Experimental claim / item | Evidence status | Notes |
|---|---|---|
| 2 × modified AgileX LIMO differential-drive robots | VERIFIED_FROM_RAW_DATA | `session_manifest.csv` lists `LIMO-01;LIMO-02`; Vicon logs are per robot. |
| Ubuntu 22.04 | MISSING_EVIDENCE | No raw file establishes the OS version. |
| ROS 2 Humble | VERIFIED_FROM_RAW_DATA | The raw metadata explicitly records `ROS 2 Humble`. |
| Intel NUC i7 onboard computers | MISSING_EVIDENCE | No raw evidence found. |
| EAI T-mini Pro 2D LiDAR | MISSING_EVIDENCE | No raw evidence found. |
| Orbbec DaBai RGB-D | MISSING_EVIDENCE | No raw evidence found. |
| RYLR998 LoRa | VERIFIED_FROM_RAW_DATA | `hardware_execution_status.csv` and provenance metadata record RYLR998. |
| 868 MHz | MISMATCH | Raw evidence records `433 MHz`; manuscript states `868 MHz`. |
| Vicon motion capture ground truth | VERIFIED_FROM_RAW_DATA | Vicon CSV logs are present for both robots, and rosbag topics include `/vicon/limo01/pose` and `/vicon/limo02/pose`. |
| FIFO / BACS / BACS+ | VERIFIED_FROM_RAW_DATA | Session IDs and scheduler CSV files are labeled accordingly. |
| 1% duty-cycle condition | MISSING_EVIDENCE | No explicit file records or raw metadata field for this exact regulatory condition. |
| `W = 60 s` scheduling window | MISSING_EVIDENCE | No explicit raw evidence for the scheduler window parameter. |
| 10 matched runs per policy | VERIFIED_FROM_RAW_DATA | `session_manifest.csv` and derived provenance files declare `n_runs = 10`; each FIFO, BACS, and BACS+ scheduler log contains run labels `1` through `10`. |
| Session duration of 720 s | VERIFIED_FROM_RAW_DATA | ROS bag metadata records `duration.nanoseconds` consistent with 720 s. |
| raw ROS DB3/MCAP contents | VERIFIED_FROM_RAW_DATA | All three sessions have DB3 and MCAP bags with consistent topic schemas and counts. |
| Vicon CSV schema | VERIFIED_FROM_RAW_DATA | Header is `timestamp_ns,x,y,z,roll_rad,pitch_rad,yaw_rad,vx,vy,vz`. |
| scheduler CSV schema | VERIFIED_FROM_RAW_DATA | Header includes `session,run,seq,policy,robot,t_gen_ns,t_selected_ns,t_tx_ns,t_rx_ns,deferral_ns,channel,rssi_dbm,snr_db,payload_hex`. |
| ROS topic names | VERIFIED_FROM_RAW_DATA | Topics match the archival metadata and bag tables: `/vicon/limo01/pose`, `/vicon/limo02/pose`, `/odom/limo01`, `/odom/limo02`, `/scan/limo01`, `/scan/limo02`, `/tf`, `/bacs/scheduler`. |
| RSSI/SNR measurements | VERIFIED_FROM_RAW_DATA | Scheduler logs contain `rssi_dbm` and `snr_db`. |
| LoRa packet information | VERIFIED_FROM_RAW_DATA | Scheduler logs include `payload_hex`, `channel`, `t_tx_ns`, `t_rx_ns`, `deferral_ns`. |
| generated/transmitted constraint counts | VERIFIED_FROM_RAW_DATA | Scheduler logs show `seq` with policy-specific counts and bag message totals. |
| scheduler overhead | MISSING_EVIDENCE | No explicit overhead table or trace is supplied beyond deferral and channel timing fields. |
| map-alignment RMSE | MISSING_EVIDENCE | No raw metric file quantifies map-alignment RMSE. |
| pose RMSE | MISSING_EVIDENCE | No raw metric file quantifies per-step trajectory pose RMSE. |
| `T_defer` | VERIFIED_FROM_RAW_DATA | Scheduler log field `deferral_ns` is present; it maps to the deferral timescale. |
| `T_channel` | VERIFIED_FROM_RAW_DATA | Scheduler log field `channel` is present, with `t_tx_ns` and `t_rx_ns` capturing transmission timing. |
| packet age | VERIFIED_FROM_RAW_DATA | Scheduler logs record `t_gen_ns`, `t_selected_ns`, `t_tx_ns`, `t_rx_ns` and deferral interval. |
| airtime utilisation | DOCUMENTED_ONLY | The manuscript discusses it, but the raw evidence does not provide a direct airtime-utilisation summary file. |
| acquisition month `2026-07` | VERIFIED_FROM_RAW_DATA | Provenance files and metadata indicate July 2026. |
| acquisition exact time | DOCUMENTED_ONLY / MISSING_EVIDENCE | Exact start timestamps exist for each ROS session, but the archive metadata says the lab-access granularity is month-level and exact time is not verifiable for the whole lab record. |
| file timestamps vs archive creation date | VERIFIED_FROM_RAW_DATA | Derived `provenance.log` and `check_provenance_crossref.csv` distinguish processing and archive dates. |
| duplicate or cloned message streams across policies | VERIFIED_FROM_RAW_DATA (no duplicates) | Hash comparison across scheduler payload streams shows no duplicate payload stream across FIFO, BACS, and BACS+. |

## Classification legend
- VERIFIED_FROM_RAW_DATA: directly supported by archival files.
- REPRODUCIBLE_FROM_CODE: would be reproducible if code were present and consistent with evidence.
- DOCUMENTED_ONLY: described in the manuscript but not independently encoded in the raw evidence.
- MISMATCH: claim disagrees with the raw evidence.
- MISSING_EVIDENCE: no independent evidence was found.

## Conclusion
The raw archive supports the core physical-validation claim that sessions were recorded in July 2026 with ROS 2 Humble, Vicon ground truth, RYLR998 radios, FIFO/BACS/BACS+ policies, ten labeled runs per policy, and session-level timing metadata. It does not support the assertions about `868 MHz`, the exact 1% duty-cycle condition, the explicit 60 s scheduling window, or the detailed Table 6 RMSE metrics without additional processing tables or estimator outputs. The manuscript and raw archive therefore agree on the ten-run count but disagree on at least one concrete hardware parameter: radio frequency.
