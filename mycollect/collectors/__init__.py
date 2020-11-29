"""
Collector module
"""
import abc

class Collector(metaclass=abc.ABCMeta):
    """Base collector class
    """

    def __init(self):
        self._collector_name = None
        self._callback = None


    @abc.abstractmethod
    def start(self) -> None:
        """Starts collecting items
        """

    @abc.abstractmethod
    def check_status(self) -> None:
        """Method called to check the status of the collect
        """

    @abc.abstractmethod
    def stop(self) -> None:
        """Stops collecting items
        """

    def emit(self, collector_name, item) -> None:
        """
            Emit a new item
        """
        self._callback(collector_name, item)

    def set_callback(self, callback) -> None:
        """
            Sets the callback that will be triggered
            when an item is emitted
        """
        self._callback = callback