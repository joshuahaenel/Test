from backend import screen_time_store


def test_log_entry_and_history():
    conn = screen_time_store.get_connection(":memory:")
    screen_time_store.log_entry(200, entry_date="2026-07-01", conn=conn)
    screen_time_store.log_entry(150, entry_date="2026-07-02", conn=conn)

    history = screen_time_store.get_history(days=7, conn=conn)

    assert history == [
        {"date": "2026-07-02", "minutes": 150},
        {"date": "2026-07-01", "minutes": 200},
    ]


def test_log_entry_upserts_same_date():
    conn = screen_time_store.get_connection(":memory:")
    screen_time_store.log_entry(100, entry_date="2026-07-01", conn=conn)
    screen_time_store.log_entry(180, entry_date="2026-07-01", conn=conn)

    history = screen_time_store.get_history(conn=conn)

    assert history == [{"date": "2026-07-01", "minutes": 180}]


def test_get_history_empty():
    conn = screen_time_store.get_connection(":memory:")
    assert screen_time_store.get_history(conn=conn) == []
