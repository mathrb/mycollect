
from mycollect.processors.url_grabber_processor import UrlGrabberProcessor
from mycollect.structures import MyCollectItem

def test_grab_url():
    processor = UrlGrabberProcessor()
    item = MyCollectItem(url="")
    updated = processor.update_item(item)
    assert "article" not in updated.extra
    item.url = "https://fr.wikipedia.org/wiki/Lille"
    updated = processor.update_item(item)
    assert "article" in updated.extra
    assert updated.extra["article"]["title"] == "Lille"