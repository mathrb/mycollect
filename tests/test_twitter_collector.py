"""Tests the twitter collector
"""

import json

from mycollect.collectors.twitter_collector import TwitterCollector


def test_get_category():
    """Tests get category
    """
    sample_tweet = json.load(open("tests/test_files/sample_tweet.json"))
    collector = TwitterCollector(None, None, None, None, None, None, [])
    category = collector.get_category(sample_tweet)
    assert not category
    collector = TwitterCollector(
        None, None, None, None, None, None, ["free steam game"])
    category = collector.get_category(sample_tweet)
    assert category
    assert category == "free steam game"
    collector = TwitterCollector(None, None, None, None, None, None, [
                                 "free steam", "free steam game"])
    category = collector.get_category(sample_tweet)
    assert category
    assert category == "free steam game"


def test_get_url():
    """Test get url
    """
    collector = TwitterCollector(None, None, None, None, None, [
        "t.co",
        "twitter.com"
    ], None)
    sample_tweet = json.load(open("tests/test_files/sample_tweet.json"))
    url = collector.get_url_from_tweet(sample_tweet)
    assert url
    url_test = json.load(open("tests/test_files/url_test.json"))
    url = collector.get_url_from_tweet(url_test)
    assert url
    assert url == "https://msft.it/6010Tg0qC"

def test_get_raw_data():
    collector = TwitterCollector(None, None, None, None, None, [
        "t.co",
        "twitter.com"
    ], ["drone"])
    def on_callback(item):
        assert item
    collector.set_callback(on_callback)
    sample_tweet = ''.join(open("tests/test_files/sample_tweet.json"))
    assert collector.on_data(sample_tweet)