"""Twitter API collection implementation
"""
from threading import Thread

from TwitterAPI import TwitterAPI

from mycollect.collectors import Collector
from mycollect.logger import create_logger
from mycollect.structures import MyCollectItem
from mycollect.utils import unshorten_url


class TwitterAPICollector(Collector):

    """Twitter collector, based on TwitterAPI streaming
    """

    def __init__(self, consumer_key, consumer_secret, languages, track):
        super().__init__()
        self._logger = create_logger().bind(collector='twitter')
        self._languages = languages
        self._api = TwitterAPI(consumer_key, consumer_secret,
                               auth_type='oAuth2', api_version='2')
        self._track = track
        self._twitter_thread = None

    def check_status(self):
        """Check status of this collect
        """
        if self._twitter_thread and not self._twitter_thread.isAlive():
            self.start()

    def start(self):
        """Starts the twitter collect
        """
        try:
            self._register_rules()
            self._twitter_thread = Thread(target=self._collect, daemon=True)
            self._twitter_thread.start()
        except Exception as err:  # pylint:disable=broad-except
            self._logger.exception(err)

    def _collect(self):
        """Starts collecting from the twitter stream
        """
        try:
            response = self._api.request('tweets/search/stream', params={
                "tweet.fields": "lang,entities",
                "media.fields": "url,preview_image_url",
                "user.fields": "id"
            })
            for item in response:
                my_collect_item = self._data_to_my_collect_item(
                    item, self._logger)
                self.emit(my_collect_item)
                if not self._twitter_thread:
                    break
            self._logger.info("closing twitter stream")
            response.close()
        except Exception as err:  # pylint:disable=broad-except
            self._logger.exception(err)

    @staticmethod
    def _data_to_my_collect_item(data: dict, logger) -> MyCollectItem:
        """Transform a tweet to a MyCollectItem

        Args:
            data (dict): tweet

        Returns:
            MyCollectItem: my collect item
        """
        url: str = None
        try:
            url = data["data"]["entities"]["urls"][0]["expanded_url"]
            url = unshorten_url(url)
        except KeyError as err:
            logger.error("key missing in tweet", key=err)
        except IndexError:
            logger.error("urls without url")
        item = MyCollectItem(
            "twitter",
            data["matching_rules"][0]["tag"],
            data["data"]["text"],
            url
        )
        item.extra["tweet"] = data
        return item

    def _register_rules(self):
        """Update the streaming rules
        """
        rules = [{'value': t, 'tag': t} for t in self._track]
        response = self._api.request(
            "tweets/search/stream/rules", method_override='GET')
        j_response = response.json()
        if "data" in j_response:
            delete_rules = [r["id"] for r in response.json()["data"]]
            self._api.request("tweets/search/stream/rules",
                              {"delete": {"ids": delete_rules}})
        response = self._api.request(
            "tweets/search/stream/rules", {"add": rules})
        if response.status_code > 201:
            self._logger.error("failed on setting rules",
                               code=response.status_code, text=response.text)
            raise Exception("Unable to set twitter rules")
        self._logger.info("rules added", rules=response.text)

    def stop(self):
        """Stops the twitter stream
        """
        local_thread = self._twitter_thread
        self._twitter_thread = None
        local_thread.join()
