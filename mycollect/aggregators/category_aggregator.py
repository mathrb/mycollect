"""
The dummy aggregator reads data from the last day and elect the top n articles per category
"""
from collections import defaultdict
from typing import Iterable

from mycollect.aggregators import Aggregator
from mycollect.structures import MyCollectItem
from mycollect.logger import create_logger


class CategoryAggregator(Aggregator):  # pylint: disable=R0903
    """Aggregates item to a basic category list with top x items
    """

    def __init__(self, top_articles=3, **kwargs):
        super().__init__(**kwargs)
        self._top_articles = top_articles
        self._logger = create_logger()

    def aggregates(self, items: Iterable[MyCollectItem]):
        categories = defaultdict(dict)
        item_count = 0
        for mycollect_item in items:
            item_count += 1
            if mycollect_item.url not in categories[mycollect_item.category]:
                categories[mycollect_item.category][mycollect_item.url] = []
            categories[mycollect_item.category][mycollect_item.url].append(
                mycollect_item)
        logger = self._logger.bind(mycollect_items=item_count)
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
        logger.info("dummy aggregation done", categories=len(results))
        return results
