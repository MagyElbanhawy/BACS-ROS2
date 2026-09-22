# BACS reproducibility repository

This repository preserves the raw physical for the paper:

"Observability- and Bandwidth-Aware Constraint Scheduling for Trust-Weighted Multi-Robot Map Fusion under Duty-Cycle-Limited Wireless Links"

It is organized to keep the raw hardware data immutable while adding validation and analysis tooling.

## Repository structure

- `AUDIT_REPORT.md` — audit of manuscript claims against the raw evidence.
- `hardware/raw/BACS_v10_raw/` — immutable extracted hardware archive.
- `hardware/SHA256SUMS.txt` — SHA-256 inventory for all archived data.
- `hardware/RAW_DATA_README.md` — raw-data provenance and file-content summary.
- `hardware/rylr998_datasheet_params.yaml` — datasheet-backed reference parameters for the RYLR998 module.
- `hardware/lora_rssi_snr_reference.csv` — lightweight schema reference for LoRa RSSI/SNR logs.
- `hardware/manifests/` — machine-readable per-session manifests.
- `hardware/tools/validate_hardware_dataset.py` — validation script for bag integrity, CSV schema, timestamps, and duplicate-stream detection.
- `hardware/validation_report.json` and `.md` — generated validation reports.
- `third_party/` — curated external references for Vicon and RYLR998 only.
- `analysis/physical/` — analysis utilities for Vicon parsing, scheduler logs, timestamps, and RMSE computation.

