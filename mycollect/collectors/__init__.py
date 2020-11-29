"""
Collector module
"""
import abc

class Collector(metaclass=abc.ABCMeta):
    """Base collector class
    """

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
