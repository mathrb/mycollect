import os
import datetime
import pytest
import json

from mycollect.data_manager.file_data_manager import FileDataManager

def test_store_data(tmp_path):
    d = tmp_path / "test"
    d.mkdir()
    fdm = FileDataManager(d)
    fdm.store_raw_data("foo", "bar")
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
    assert value["data"] == "bar"

def test_read_data(tmp_path):
    d = tmp_path / "test"
    d.mkdir()
    fdm = FileDataManager(d)
    print("x")
    timestamp = round(datetime.datetime.now().timestamp())
    for i in range(987):
        fdm.store_raw_data("foo", i)
    i = 0
    for item in fdm.read_raw_data("foo", timestamp):
        assert i == item
        i += 1
    assert i == 987