from backend import health_store

SAMPLE_PAYLOAD = {
    "data": {
        "metrics": [
            {
                "name": "step_count",
                "units": "count",
                "data": [{"date": "2026-07-01 08:00:00 +0000", "qty": 4231}],
            },
            {
                "name": "heart_rate",
                "units": "bpm",
                "data": [{"date": "2026-07-01 08:00:00 +0000", "qty": 62}],
            },
        ]
    }
}


def test_store_and_read_latest():
    conn = health_store.get_connection(":memory:")
    inserted = health_store.store_payload(SAMPLE_PAYLOAD, conn=conn)
    assert inserted == 2

    summary = health_store.latest_summary(conn=conn)
    metrics_by_name = {m["metric"]: m for m in summary["metrics"]}
    assert metrics_by_name["step_count"]["value"] == 4231
    assert metrics_by_name["heart_rate"]["value"] == 62


def test_latest_summary_empty():
    conn = health_store.get_connection(":memory:")
    summary = health_store.latest_summary(conn=conn)
    assert summary["metrics"] == []


def test_store_payload_ignores_malformed_entries():
    conn = health_store.get_connection(":memory:")
    payload = {"data": {"metrics": [{"name": "steps", "data": [{"qty": None, "date": "x"}]}]}}
    inserted = health_store.store_payload(payload, conn=conn)
    assert inserted == 0


def test_recent_samples_filters_by_metric():
    conn = health_store.get_connection(":memory:")
    health_store.store_payload(SAMPLE_PAYLOAD, conn=conn)
    samples = health_store.recent_samples(metric="step_count", conn=conn)
    assert len(samples) == 1
    assert samples[0]["metric"] == "step_count"
