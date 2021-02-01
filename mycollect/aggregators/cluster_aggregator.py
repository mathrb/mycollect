"""Cluster aggregator
https://github.com/adjidieng/ETM ?
"""
from typing import Iterable

from mycollect.aggregators import Aggregator
from mycollect.structures import MyCollectItem
from mycollect.logger import create_logger

class ClusterAggregator(Aggregator):

    """Cluster aggregator class
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def aggregates(self, items: Iterable[MyCollectItem]):
        articles = [i for i in items if "article" in i.extra]
        
