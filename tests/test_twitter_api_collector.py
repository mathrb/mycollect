
import pytest

from mycollect.structures import MyCollectItem
from mycollect.collectors.twitter_api_collector import TwitterAPICollector


def test_twitter_api_collector():
    with pytest.raises(Exception):
        TwitterAPICollector(None, None, None, None)
    with pytest.raises(Exception):
        TwitterAPICollector("abc", "def", ["en"], ["foo", "bar"])


def test_data_to_my_collect():
    data = {
        "data": {
            "text": "Hello world",

        },
        "matching_rules": [
            {
                "tag": "hello_world"
            }
        ]
    }
    item = TwitterAPICollector.data_to_my_collect_item(data)
    assert item.text
    assert not item.url
    assert "tweet_error_url" in item.extra
    data["data"]["entities"] = {
        "urls":[
            {
                "expanded_url": "https://www.google.fr"
            }
        ]
    }
    item = TwitterAPICollector.data_to_my_collect_item(data)
    assert item.text
    assert item.url == "https://www.google.fr"
