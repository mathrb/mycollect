"""Generic key value cache
"""
import abc
import dbm
import os
from typing import Optional


class MyCache(metaclass=abc.ABCMeta):

    """MyCache key value
    """

    def __init__(self, name: str):
        """MyCache ctor

        Args:
            name (str): name of this cache
        """
        self._name = name

    @abc.abstractmethod
    def set_item(self, key: str, value: str) -> None:
        """Sets the ket and value

        Args:
            key (str): key to insert
            value (str): value
        """

    @abc.abstractmethod
    def get_item(self, key: str) -> Optional[str]:
        """Gets the item associated with the key

        Args:
            key (str): key

        Returns:
            Optional[str]: value
        """


class DbmCache(MyCache):

    """A simple cache with dbm backend
    """

    def __init__(self, name: str, working_folder: str):
        super().__init__(name)
        self._db = dbm.open(os.path.join(working_folder, name), 'c')

    def set_item(self, key: str, value: str) -> None:
        self._db[key] = value

    def get_item(self, key: str) -> Optional[str]:
        value = self._db.get(key, None)
        if value is not None:
            return value.decode()
        return value
