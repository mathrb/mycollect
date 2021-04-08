"""Twitter API collection implementation
"""
from dataclasses import dataclass
from threading import Thread
import datetime

from TwitterAPI import TwitterAPI  # type:ignore

from mycollect.collectors import Collector
from mycollect.logger import create_logger
from mycollect.structures import MyCollectItem
from mycollect.utils import unshorten_url


@dataclass
class TwitterDelays():

    """Container for timers
    """

    last_tweet_received: datetime.datetime
    last_reconnection_attempt: datetime.datetime

    def last_tweet_from_now(self) -> float:
        """Seconds elapsed from the last tweet received

        Returns:
            float: Seconds elapsed from the last tweet received
        """
        return (datetime.datetime.now() - self.last_tweet_received).total_seconds()

    def last_reconnection_attempt_from_now(self) -> float:
        """Seconds elapsed from the last reconnection attempt

        Returns:
            float: Seconds elapsed from the last reconnection attempt
        """
        return (datetime.datetime.now() - self.last_reconnection_attempt).total_seconds()

    def update_tweet_received(self):
        """Update the last tweet received time
        """
        self.last_tweet_received = datetime.datetime.now()

    def update_reconnection_attempt(self):
        """Update the last reconnection attempt time
        """
        self.last_reconnection_attempt = datetime.datetime.now()


class TwitterAPICollector(Collector):

    """Twitter collector, based on TwitterAPI streaming
    """

    BASE_RULES = " has:links"

    def __init__(self, consumer_key, consumer_secret, languages, track):
        super().__init__()
        self._logger = create_logger().bind(collector='twitter')
        self._base_rule = TwitterAPICollector.BASE_RULES
        lang_rule = []
        for language in languages:
            lang_rule.append("lang:" + language)
        self._base_rule += " (" + " OR ".join(lang_rule) + ")"
        self._track = track
        self._thread = None
        self._api = TwitterAPI(consumer_key, consumer_secret,
                               auth_type='oAuth2', api_version='2')
        self._twitter_delays = TwitterDelays()

    def check_status(self):
        """Check status of this collect
        """
        self._logger.debug("check status",
                           thread_is_null=self._thread is None,
                           thread_is_alive=False if not self._thread else self._thread.is_alive(),
                           should_reconnect=self.should_reconnect(),
                           last_tweet=self._twitter_delays.last_tweet_from_now())
        if self._thread and not self._thread.is_alive() and self.should_reconnect():
            self._logger.info("trigger reconnection")
            self.start()
        elif self._twitter_delays.last_tweet_from_now() > 60 * 5:
            self._logger.info("trigger reconnection")
            self.start()

    def should_reconnect(self) -> bool:
        """Wethere we should reconnect the twitter stream or not

        Returns:
            bool: True if we should reconnect, False otherwise
        """
        return self._twitter_delays.last_reconnection_attempt_from_now() > 60 * 5

    def start(self):
        """Starts the twitter collect
        """
        try:
            if self._thread:
                self._logger.info("stopping collection")
                self.stop()
                self._logger.info("collection stopped")
            self._twitter_delays.update_reconnection_attempt()
            self._register_rules()
            self._thread = Thread(target=self._collect, daemon=True)
            self._thread.start()
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
                self._twitter_delays.update_tweet_received()
                my_collect_item = self.data_to_my_collect_item(item)
                self.emit(my_collect_item)
                if not self._thread:
                    break
            self._logger.info("closing twitter stream")
            response.close()
        except Exception as err:  # pylint:disable=broad-except
            self._logger.exception(err)

    @staticmethod
    def data_to_my_collect_item(data: dict) -> MyCollectItem:
        """Transform a tweet to a MyCollectItem

        Args:
            data (dict): tweet

        Returns:
            MyCollectItem: my collect item
        """
        item = MyCollectItem(
            "twitter",
            data["matching_rules"][0]["tag"],
            data["data"]["text"]
        )

        try:
            url = data["data"]["entities"]["urls"][0]["expanded_url"]
            item.url = unshorten_url(url)
        except KeyError as err:
            item.extra["tweet_error_url"] = f"Key missing {err}"
        except IndexError:
            item.extra["tweet_error_url"] = "urls without url"

        item.extra["tweet"] = data
        return item

    def _register_rules(self):
        """Update the streaming rules
        """
        rules = [{'value': t + self._base_rule, 'tag': t} for t in self._track]
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
        local_thread = self._thread
        self._thread = None
        local_thread.join()
