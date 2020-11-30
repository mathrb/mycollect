import os
import datetime
import pytest
import json

from mycollect.storage.file_storage import FileStorage
from mycollect.structures import MyCollectItem

def test_store_data(tmp_path):
    d = tmp_path / "test"
    d.mkdir()
    fdm = FileStorage(d)
    fdm.store_item(MyCollectItem("foo", "bar", "hello", "world"))
    assert os.path.exists(os.path.join(d, "foo"))
    dt = datetime.datetime.now()
    filename = "{}_{}_{}.jsonl".format(dt.year, dt.month, dt.day)
    assert os.path.exists(os.path.join(d, "foo", filename))
    lines = list(open(os.path.join(d, "foo", filename)))
    assert 1 == len(lines)
    value = json.loads(lines[0])
    assert "timestamp" in value
    assert value["timestamp"] >= round(dt.timestamp())
    assert value["timestamp"] <= round(datetime.datetime.now().timestamp())
    assert value["data"]["category"] == "bar"

def test_read_data(tmp_path):
    d = tmp_path / "test"
    d.mkdir()
    fdm = FileStorage(d)
    print("x")
    timestamp = round(datetime.datetime.now().timestamp())
    for i in range(987):
        fdm.store_item(MyCollectItem("foo", str(i), "cat", "url"))
    i = 0
    for item in fdm.fetch_items(timestamp):
        assert str(i) == item.category
        i += 1
    assert i == 987