from mycollect import cache

def test_dbm_cache(tmp_path):
    my_cache = cache.DbmCache("test", str(tmp_path))
    b = my_cache.get_item("a")
    assert b is None
    my_cache.set_item("a", "b")
    b = my_cache.get_item("a")
    assert b == "b"