import pytest

from mycollect.aggregators.category_aggregator import CategoryAggregator
from mycollect.structures import MyCollectItem

def test_dummy_aggregator(load_mycollect_items):
    dummy = CategoryAggregator()
    result = dummy.aggregates(load_mycollect_items)
    assert result == {}
    
@pytest.mark.file("tests/test_files/twitter/agg_test_1.jsonl")
def test_dummy_aggregator_1(load_mycollect_items):
    dummy = CategoryAggregator()
    result = dummy.aggregates(load_mycollect_items)
    for item in load_mycollect_items:
        assert item.category in result
