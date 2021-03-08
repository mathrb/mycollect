"""Last processor
"""

from typing import Optional, List

from mycollect.processors import Processor
from mycollect.storage import Storage
from mycollect.structures import MyCollectItem


class ExitProcessor(Processor):#pylint:disable=R0903
    """Last processor that use storage to save the item
    """

    def __init__(self, storages: List[Storage]):
        if not storages:
            raise ValueError("storages")
        if not isinstance(storages, list):
            storages = [storages]
        self._storages: List[Storage] = storages

    def update_item(self, item: MyCollectItem) -> Optional[MyCollectItem]: # type:ignore
        """
            Updates the current MyCollectItem, return None to drop this item
        """
        for storage in self._storages:
            storage.store_item(item)
