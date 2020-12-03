"""Defines structures used in mycollect
"""


class MyCollectItem():
    """Represents an item being shared per sections
    """

    def __init__(self, provider: str = None, category: str = None,
                 text: str = None, url: str = None):
        self._category = category
        self._text = text
        self._url = url
        self._provider = provider
        self._extra = {}

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
    def extra(self) -> dict:
        """Returns the extended data of this item
        """
        return self._extra

    @property
    def provider(self) -> str:
        """Gets the provider of this item
        """
        return self._provider

    def to_dict(self) -> dict:
        """Returns the dict form of this object

        Returns:
            dict: This object as dict
        """
        return {
            "category": self._category,
            "provider": self._provider,
            "text": self._text,
            "url": self._url,
            "extra": self._extra
        }

    @staticmethod
    def from_dict(item: dict):
        """Creates a new MyCollectItem instance based on input dict

        Args:
            item (dict): MyCollectItem as dict

        Returns:
            MyCollectItem: the MyCollectItem created
        """
        my_collect_item = MyCollectItem(
            provider=item["provider"],
            category=item["category"],
            text=item["text"],
            url=item["url"]
        )
        if "extra" in item:
            my_collect_item.extra.update(item["extra"])
        return my_collect_item
