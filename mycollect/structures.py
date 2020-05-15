"""Defines structures used in mycollect
"""


class MyCollectItem():
    """Represents an item being shared per sections
    """

    def __init__(self, category: str = None, text: str = None, url: str = None):
        self._category = category
        self._text = text
        self._url = url
        self._extended_data = None

    @property
    def category(self):
        """Returns the category of this item
        """
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @property
    def text(self):
        """Returns the text belonging to this item
        """
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def url(self):
        """Returns the url of this item
        """
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def extended_data(self):
        """Returns the extended data of this item
        """
        return self._extended_data

    @extended_data.setter
    def extended_data(self, value):
        self._extended_data = value
