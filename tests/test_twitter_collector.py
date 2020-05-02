"""Tests the twitter collector
"""

import json

from oracle.collectors.twitter_collector import TwitterCollector

def test_get_category():
    """Tests get category
    """
    sample_tweet = json.load(open("tests/test_files/sample_tweet.json"))
    collector = TwitterCollector(None, None, None, None, None, None, None, [])
    category = collector.get_category(sample_tweet)
    assert not category
    collector = TwitterCollector(None, None, None, None, None, None, None, ["free steam game"])
    category = collector.get_category(sample_tweet)
    assert category
    assert category == "free steam game"
    collector = TwitterCollector(None, None, None, None, None, None, None, ["free steam", "free steam game"])
    category = collector.get_category(sample_tweet)
    assert category
    assert category == "free steam game"
