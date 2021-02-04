"""Last processor
"""

from typing import Optional

from mycollect.processors import Processor
from mycollect.storage import Storage
from mycollect.structures import MyCollectItem


class ExitProcessor(Processor):#pylint:disable=R0903
    """Last processor that use storage to save the item
    """

    def __init__(self, storage: Storage):
        self._storage: Storage = storage

    def update_item(self, item: MyCollectItem) -> Optional[MyCollectItem]: # type:ignore
        """
            Updates the current MyCollectItem, return None to drop this item
        """
        self._storage.store_item(item)
