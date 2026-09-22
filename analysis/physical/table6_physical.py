"""Audit the physical Table 6 claims against the available raw archive.

The raw archive contains scheduler diagnostics and Vicon ground truth, but no
per-run map-alignment estimates. This script therefore reports the manuscript
RMSE targets as unavailable for independent recomputation and computes only
diagnostics that are directly present in scheduler CSV logs.
"""
from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path
from typing import Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "hardware" / "raw" / "BACS_v10_raw" / "experiment_results" / "bacs_logs"
OUT_DIR = ROOT / "paper_results"

TARGETS = {
    "FIFO": {"mean_m": 0.48, "std_m": 0.15},
    "BACS": {"mean_m": 0.28, "std_m": 0.08},
    "BACS+": {"mean_m": 0.27, "std_m": 0.09},
}

PAPER_DIAGNOSTIC_TARGETS = {
    "median_scheduling_deferral_s": 154.0,
    "median_channel_delay_s": 0.17,
    "deferral_to_channel_ratio": 906.0,
}


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.fmean(values) if values else float("nan")


def _read(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def audit() -> Dict[str, object]:
    diagnostics = []
    for path in sorted(LOG_DIR.glob("*.csv")):
        rows = _read(path)
        if not rows:
            continue
        policy = rows[0]["policy"]
        deferral = [int(row["deferral_ns"]) / 1e9 for row in rows]
        channel = [
            (int(row["t_rx_ns"]) - int(row["t_tx_ns"])) / 1e9
            for row in rows
        ]
        runs = sorted({int(row["run"]) for row in rows})
        diagnostics.append(
            {
                "policy": policy,
                "source": str(path.relative_to(ROOT)),
                "events": len(rows),
                "run_labels": runs,
                "run_label_count": len(runs),
                "deferral_mean_s": _mean(deferral),
                "deferral_median_s": statistics.median(deferral),
                "channel_delay_mean_s": _mean(channel),
                "channel_delay_median_s": statistics.median(channel),
                "rssi_mean_dbm": _mean(float(row["rssi_dbm"]) for row in rows),
                "snr_mean_db": _mean(float(row["snr_db"]) for row in rows),
            }
        )

    return {
        "status": "incomplete_from_archive",
        "rmse_status": "unavailable_without_per_run_map_alignment_metrics",
        "paper_targets": TARGETS,
        "paper_diagnostic_targets": PAPER_DIAGNOSTIC_TARGETS,
        "diagnostic_target_status": (
            "not_reproduced: the current scheduler logs contain timing fields, "
            "but their observed scales do not independently recover the paper targets"
        ),
        "diagnostics": diagnostics,
        "required_missing_inputs": [
            "per-run map-alignment RMSE values or map-estimate streams",
            "a documented mapping from raw bag topics to the Table 6 estimator",
        ],
    }


def main() -> None:
    report = audit()
    OUT_DIR.mkdir(exist_ok=True)
    json_path = OUT_DIR / "physical_table6_audit.json"
    csv_path = OUT_DIR / "physical_communication_diagnostics.csv"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        rows = report["diagnostics"]
        fields = list(rows[0]) if rows else []
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"RMSE status: {report['rmse_status']}")
    print(f"-> {json_path.relative_to(ROOT)}")
    print(f"-> {csv_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
