"""
Processor that will get the content of a webpage
"""

from typing import Optional

from newspaper.article import Article, ArticleDownloadState

from mycollect.processors import Processor
from mycollect.structures import MyCollectItem


class UrlGrabberProcessor(Processor):  # pylint:disable=too-few-public-methods

    """Grab the content defined in the url of the MyCollectItem
    """

    def update_item(self, item: MyCollectItem) -> Optional[MyCollectItem]:
        """
            Updates the current MyCollectItem, return None to drop this item
        """
        article = Article(item.url)
        try:
            article.download()
            article.parse()
        except Exception as err:  # pylint:disable=broad-except
            print(err)
        if article.download_state == ArticleDownloadState.SUCCESS:
            item.extra["article"] = {
                "text": article.text,
                "title": article.title,
                "keywords": article.keywords
            }
        return item
