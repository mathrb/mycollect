"""
    Processors will update the mycollectitem through the pipeline
"""
import abc
from typing import List, Optional
from mycollect.structures import MyCollectItem
from mycollect.logger import create_logger


class Processor(metaclass=abc.ABCMeta):  # pylint:disable=R0903
    """Transforms a MyCollectItem
    """

    @abc.abstractmethod
    def update_item(self, item: MyCollectItem) -> Optional[MyCollectItem]:
        """
            Updates the current MyCollectItem, return None to drop this item
        """


class PipelineProcessor(Processor):
    """Pipeline that manages processors
    """

    def __init__(self):
        self._processors: List[Processor] = []
        self._logger = create_logger()

    def append_processor(self, processor: Processor) -> None:
        """Add a processor to the list

        Args:
            processor (Processor): processor
        """
        self._processors.append(processor)

    def update_item(self, item: MyCollectItem) -> Optional[MyCollectItem]:
        """Updates an item using the processors

        Args:
            item (MyCollectItem): MyCollectItem

        Returns:
            MyCollectItem: The updated item
        """
        new_item = item
        for processor in self._processors:
            try:
                new_item = processor.update_item(item) # type: ignore
                if not new_item:
                    break
            except Exception as err:  # pylint:disable=broad-except
                self._logger.exception(err)
        return new_item
