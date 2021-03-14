"""
Processor that will get the content of a webpage
"""
import json
from typing import Optional
from urllib.parse import urlparse

import cloudscraper #type: ignore
from newspaper.article import (Article, ArticleDownloadState,  # type: ignore
                               Configuration)

from mycollect.cache import DbmCache
from mycollect.logger import create_logger
from mycollect.processors import Processor
from mycollect.structures import MyCollectItem


INVALID_URL_NEWS = [
    "https://twitter.com",
    "https://youtu.be"
]


class UrlGrabberProcessor(Processor):  # pylint:disable=too-few-public-methods

    """Grab the content defined in the url of the MyCollectItem
    """

    def __init__(self):
        super().__init__()
        self._logger = create_logger()
        self._cache = DbmCache("url_grab")
        self._cloudscrapper = cloudscraper.create_scraper()

    def update_item(self, item: MyCollectItem) -> Optional[MyCollectItem]:
        """
            Updates the current MyCollectItem, return None to drop this item
        """
        if self._is_valid(item.url):
            cache_article = self._cache.get_item(item.url)
            if not cache_article:
                user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0)' \
                    ' Gecko/20100101 Firefox/85.0'
                config = Configuration()
                config.browser_user_agent = user_agent
                article = Article(item.url, config=config)
                try:
                    article.download(recursion_counter=2)
                    if article.download_state == 1 and '403' in article.download_exception_msg:
                        article = self._cloudscrap(article)
                    if article.download_state == ArticleDownloadState.SUCCESS:
                        article.parse()
                except Exception as err:  # pylint:disable=broad-except
                    self._logger.error(
                        "Unable to download article", error=str(err))
                    self._logger.debug(err)
                else:
                    if article.download_state == ArticleDownloadState.SUCCESS:
                        cache_article = {
                            "text": article.text,
                            "title": article.title,
                            "keywords": article.keywords
                        }

                        links = [item.url]
                        if article.canonical_link:
                            links.append(article.canonical_link)
                            item.extra["origin_url"] = item.url
                            item.url = article.canonical_link
                        self._add_to_cache(cache_article, links)
                    else:
                        self._logger.warning("download state",
                                             state=article.download_state,
                                             url=item.url,
                                             error_message=article.download_exception_msg)
            else:
                cache_article = json.loads(cache_article)
            if cache_article:
                item.extra["article"] = cache_article
        return item

    def _cloudscrap(self, article: Article) -> Article:
        article_response = self._cloudscrapper.get(article.url)
        if article_response.status_code == 200:
            article.set_html(article_response.text)
        else:
            article.download_state = article_response.status_code
            article.download_exception_msg = article_response.reason
        return article

    def _add_to_cache(self, item: dict, links: list):
        json_data = json.dumps(item)
        for link in links:
            self._cache.set_item(link, json_data)

    @staticmethod
    def _is_valid(url):
        parsed_url = urlparse(url)
        if parsed_url.scheme and parsed_url.netloc:
            for invalid in INVALID_URL_NEWS:
                if invalid in url:
                    return False
            return True
        return False
