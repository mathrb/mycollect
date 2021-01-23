"""
Processor that will get the content of a webpage
"""
from typing import Optional

from newspaper.article import Article, ArticleDownloadState

from mycollect.logger import create_logger
from mycollect.processors import Processor
from mycollect.structures import MyCollectItem

INVALID_URL_NEWS = [
    "https://twitter.com/i/web/status"
]


class UrlGrabberProcessor(Processor):  # pylint:disable=too-few-public-methods

    """Grab the content defined in the url of the MyCollectItem
    """

    def __init__(self):
        super().__init__()
        self._logger = create_logger()

    def update_item(self, item: MyCollectItem) -> Optional[MyCollectItem]:
        """
            Updates the current MyCollectItem, return None to drop this item
        """
        if not self._is_restricted(item.url):
            article = Article(item.url)
            try:
                article.download()
                article.parse()
            except Exception as err:  # pylint:disable=broad-except
                self._logger.exception(err)
            if article.download_state == ArticleDownloadState.SUCCESS:
                item.extra["article"] = {
                    "text": article.text,
                    "title": article.title,
                    "keywords": article.keywords
                }
            else:
                self._logger.warning("download state", state=article.download_state, url=item.url)
        return item

    @staticmethod
    def _is_restricted(url):
        for invalid in INVALID_URL_NEWS:
            if invalid in url:
                return True
        return False
