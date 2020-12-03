from mycollect.processors.exit_processor import ExitProcessor
from mycollect.processors import PipelineProcessor
from mycollect.storage import Storage
from mycollect.structures import MyCollectItem

class DummyStorage(Storage):

    def __init__(self):
        super().__init__()
        self._items = []

    def store_item(self, item):
        self._items.append(item)

    def fetch_items(self, timestamp):
        return self._items

def test_exit_processor():
    storage = DummyStorage()
    processor = ExitProcessor(storage)
    mci = MyCollectItem("dum", "foo", "bar")
    processor.update_item(mci)
    assert mci in storage.fetch_items(None)

def test_pipeline_processor():
    pipeline = PipelineProcessor()
    storage = DummyStorage()
    processor = ExitProcessor(storage)
    pipeline.append_processor(processor)
    mci = MyCollectItem("dum", "foo", "bar")
    pipeline.update_item(mci)
    assert mci in storage.fetch_items(None)
