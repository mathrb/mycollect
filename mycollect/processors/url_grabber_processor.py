"""
Processor that will get the content of a webpage
"""
import json
from typing import Optional

from newspaper.article import (Article, ArticleDownloadState,  # type: ignore
                               Configuration)

from mycollect.cache import DbmCache
from mycollect.logger import create_logger
from mycollect.processors import Processor
from mycollect.structures import MyCollectItem

INVALID_URL_NEWS = [
    "https://twitter.com"
]


class UrlGrabberProcessor(Processor):  # pylint:disable=too-few-public-methods

    """Grab the content defined in the url of the MyCollectItem
    """

    def __init__(self):
        super().__init__()
        self._logger = create_logger()
        self._cache = DbmCache("url_grab")

    def update_item(self, item: MyCollectItem) -> Optional[MyCollectItem]:
        """
            Updates the current MyCollectItem, return None to drop this item
        """
        if not self._is_restricted(item.url):
            cache_article = self._cache.get_item(item.url)
            if not cache_article:
                user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0)' \
                    ' Gecko/20100101 Firefox/85.0'
                config = Configuration()
                config.browser_user_agent = user_agent
                article = Article(item.url, config=config)
                try:
                    article.download(recursion_counter=2)
                    article.parse()
                except Exception as err:  # pylint:disable=broad-except
                    self._logger.exception(err)
                else:
                    if article.download_state == ArticleDownloadState.SUCCESS:
                        cache_article = {
                            "text": article.text,
                            "title": article.title,
                            "keywords": article.keywords
                        }
                        self._cache.set_item(
                            item.url, json.dumps(cache_article))
                    else:
                        self._logger.warning("download state",
                                             state=article.download_state, url=item.url)
            else:
                cache_article = json.loads(cache_article)
            if cache_article:
                item.extra["article"] = cache_article
        return item

    @staticmethod
    def _is_restricted(url):
        for invalid in INVALID_URL_NEWS:
            if invalid in url:
                return True
        return False
