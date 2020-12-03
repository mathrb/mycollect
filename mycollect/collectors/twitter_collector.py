"""Twitter collection implementation
"""
import json
from typing import Iterator, Optional
from urllib.parse import urlparse

from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener

from mycollect.collectors import Collector
from mycollect.logger import create_logger
from mycollect.structures import MyCollectItem
from mycollect.utils import unshorten_url


class TwitterCollector(StreamListener, Collector):  # pylint:disable=too-many-instance-attributes
    """Twitter collector, based on Tweepy streaming
    """

    def __init__(self, consumer_key, consumer_secret,  # pylint:disable=too-many-arguments
                 access_token, access_secret, languages, low_priority_url, track):
        super().__init__()
        self._logger = create_logger().bind(collector='twitter')
        self._track = track
        self._languages = languages
        self._low_priority_url = low_priority_url
        self._auth = OAuthHandler(consumer_key, consumer_secret)
        self._auth.set_access_token(access_token, access_secret)
        self._twitter_stream = Stream(self._auth, self)

    def start(self):
        """Collect data from twitter
        """
        self._twitter_stream.filter(
            track=self._track, languages=self._languages, is_async=True)

    def check_status(self):
        """Check the status of the collect
        """
        if not self._twitter_stream.running:
            self._logger.info("twitter collect not running, restarting")
            self.stop()
            self.start()

    def stop(self):
        """Stops the streaming
        """
        self._twitter_stream.disconnect()

    def on_data(self, raw_data):
        try:
            loaded_tweet = json.loads(raw_data)
            category = self.get_category(loaded_tweet)
            retweet = loaded_tweet.get("retweeted_status", None)
            if retweet is not None:
                url = self.get_url_from_tweet(loaded_tweet["retweeted_status"])
                if not url:
                    url = self.get_url_from_tweet(loaded_tweet)
            else:
                url = self.get_url_from_tweet(loaded_tweet)
            if url:
                try:
                    url = unshorten_url(url)
                except Exception as err:
                    self._logger.exception(str(err))
                    raise

            if url and category:
                item = MyCollectItem(provider="twitter",
                                     category=category,
                                     text=loaded_tweet.get("text", None),
                                     url=url)
                item.extra["tweet"] = loaded_tweet
                self.emit(item)
        except BaseException as err:  # pylint:disable=broad-except
            self._logger.error("on_data unexpected error: {}".format(err))
            self._logger.exception(err)
        return True

    def on_error(self, status_code):
        self._logger.error("twitter error", status=status_code)
        return True

    def get_category(self, tweet: dict) -> Optional[str]:
        """Gets the category associated to the tweet

        Arguments:
            tweet {dict} -- tweet as dict

        Returns:
            str -- category of the tweet
        """
        best_track = None
        full_text = self.get_text_for_category_selection(tweet).lower()
        for track in self._track:
            words = track.split()
            i = len(words)
            for word in words:
                if word in full_text:
                    i -= 1
            if i == 0:
                if best_track is None:
                    best_track = (track, len(words))
                elif best_track[1] < len(words):
                    best_track = (track, len(words))
        if best_track:
            return best_track[0]
        return None

    def get_url_from_tweet(self, tweet: dict) -> Optional[str]:
        """Retrieves the best url from the tweet

        Arguments:
            tweet {dict} -- tweet

        Returns:
            str -- url of the tweet
        """
        urls = set(TwitterCollector.get_url_stack(tweet))
        real_url = None
        for url in urls:
            parsed_url = urlparse(url)
            if real_url is None:
                real_url = parsed_url
            if (real_url.netloc in self._low_priority_url
                    and parsed_url.netloc not in self._low_priority_url):
                real_url = parsed_url
        return real_url.geturl() if real_url else None

    @staticmethod
    def get_url_stack(tweet: dict) -> Iterator[str]:
        """Returns all expanded urls from a tweet

        Arguments:
            tweet {dict} -- tweet

        Yields:
            str -- url
        """
        if "extended_tweet" in tweet:
            yield from TwitterCollector.get_url_stack(tweet["extended_tweet"])
        if "retweeted_status" in tweet:
            yield from TwitterCollector.get_url_stack(tweet["retweeted_status"])
        if "quoted_status" in tweet:
            yield from TwitterCollector.get_url_stack(tweet["quoted_status"])
        if "entities" in tweet:
            if "urls" in tweet["entities"]:
                for url in tweet["entities"]["urls"]:
                    if "expanded_url" in url:
                        yield url["expanded_url"]

    @staticmethod
    def get_text_for_category_selection(tweet):
        """Returns all text in which Twitter look for term matching

        Arguments:
            tweet {dict} -- tweet

        Returns:
            str -- text
        """
        text = tweet.get("text", "")
        if "extended_tweet" in tweet:
            text += tweet["extended_tweet"].get("full_text", "")
            text += TwitterCollector.get_entities_text(tweet["extended_tweet"])
        if "retweeted_status" in tweet:
            text += TwitterCollector.get_text_for_category_selection(
                tweet["retweeted_status"])
        if "quoted_status" in tweet:
            text += TwitterCollector.get_text_for_category_selection(
                tweet["quoted_status"])
        text += TwitterCollector.get_entities_text(tweet)
        return text

    @staticmethod
    def get_entities_text(tweet):
        """Gets the text from tweet entities

        Arguments:
            tweet {dict} -- tweet

        Returns:
            str -- text from entities
        """
        text = ''
        for item in tweet["entities"].get("hastags", []):
            text += item["text"] + " "
        for item in tweet["entities"].get("urls", []):
            if "expanded_url" in item:
                text += item["expanded_url"] + " "
            if "display_url" in item:
                text += item["display_url"] + " "
        for item in tweet["entities"].get("user_mentions", []):
            if "screen_name" in item:
                text += item["screen_name"] + " "
        for item in tweet["entities"].get("media", []):
            if "expanded_url" in item:
                text += item["expanded_url"] + " "
            if "display_url" in item:
                text += item["display_url"] + " "
        return text
