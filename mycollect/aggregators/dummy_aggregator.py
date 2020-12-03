"""
The dummy aggregator reads data from the last day and elect the top n articles per category
"""
from collections import defaultdict
from typing import Iterable

from mycollect.aggregators import Aggregator
from mycollect.structures import MyCollectItem


class DummyAggregator(Aggregator): #pylint: disable=R0903
    """Aggregates item to a basic category list with top x items
    """

    def __init__(self, top_articles=3):
        self._top_articles = top_articles

    def aggregates(self, items: Iterable[MyCollectItem]):
        categories = defaultdict(dict)
        for mycollect_item in items:
            if mycollect_item.url not in categories[mycollect_item.category]:
                categories[mycollect_item.category][mycollect_item.url] = []
            categories[mycollect_item.category][mycollect_item.url].append(
                mycollect_item)
        results = {}
        for category, url_dict in sorted(categories.items()):
            category_items = []
            for url, mycollect_items in url_dict.items():
                item = {
                    "url": url,
                    "count": len(mycollect_items),
                    "text": mycollect_items[0].text
                }
                category_items.append(item)
            items = sorted(
                category_items, key=lambda x: x["count"], reverse=True)
            results[category] = items[:self._top_articles]
        return results
