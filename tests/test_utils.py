
import pytest

from mycollect.utils import get_class, get_object_fqdn
from mycollect.structures import MyCollectItem

def test_get_class():
    """Test get_class
    """
    class_to_load = "mycollect.collectors.twitter_collector.TwitterCollector"
    _ = get_class(class_to_load)
    with pytest.raises(AttributeError):
        get_class("mycollect.foo")

@pytest.mark.parametrize("obj,expected", [
    (MyCollectItem(), "mycollect.structures.MyCollectItem"),
    ("hello world", "str")])
def test_get_fullname(obj, expected):
    assert get_object_fqdn(obj) == expected
