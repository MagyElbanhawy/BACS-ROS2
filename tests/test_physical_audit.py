from analysis.physical.table6_physical import audit


def test_each_policy_has_ten_labeled_runs():
    report = audit()
    assert len(report["diagnostics"]) == 3
    for row in report["diagnostics"]:
        assert row["run_labels"] == list(range(1, 11))
        assert row["run_label_count"] == 10


def test_table6_rmse_is_not_fabricated():
    report = audit()
    assert report["rmse_status"] == "unavailable_without_per_run_map_alignment_metrics"
    assert report["paper_targets"]["FIFO"] == {"mean_m": 0.48, "std_m": 0.15}
    assert report["paper_diagnostic_targets"]["median_scheduling_deferral_s"] == 154.0
