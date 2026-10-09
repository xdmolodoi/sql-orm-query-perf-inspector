from app.inspector import normalize_sql, QueryStore

def test_normalize_sql_replaces_literals():
    assert normalize_sql("SELECT * FROM books WHERE id = 42") == "select * from books where id = ?"
    assert normalize_sql("SELECT * FROM books WHERE name = 'Mira'") == "select * from books where name = ?"

def test_store_records_event():
    store = QueryStore()
    class Context: pass
    ctx = Context()
    store.before_execute(None, None, "SELECT 1", (), ctx, False)
    store.after_execute(None, None, "SELECT 1", (), ctx, False)
    assert store.summary()["total_queries"] == 1
    assert len(store.events(10)) == 1
    assert store.events(10)[0]["is_select"] is True
