
import pytest

from mycollect.utils import get_class

def test_get_class():
    """Test get_class
    """
    class_to_load = "mycollect.collectors.twitter_collector.TwitterCollector"
    _ = get_class(class_to_load)
    with pytest.raises(AttributeError):
        get_class("mycollect.foo")
