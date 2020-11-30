"""
    Processors will update the mycollectitem through the pipeline
"""
import abc
from typing import List
from mycollect.structures import MyCollectItem

class Processor(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def update_item(self, item: MyCollectItem) -> MyCollectItem:
        """
            Updates the current MyCollectItem, return None to drop this item
        """

class PipelineProcessor(Processor):

    def __init__(self):
        self._processors : List[Processor] = []

    def append_processor(self, processor: Processor) -> None:
        self._processors.append(processor)

    def update_item(self, item: MyCollectItem) -> MyCollectItem:
        new_item = item
        for processor in self._processors:
            new_item = processor.update_item(item)
            if not new_item:
                break
        return new_item
