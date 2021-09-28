"""Twitter collection implementation
"""
import json
from typing import Iterator, Optional, List, Dict, Tuple
from urllib.parse import urlparse
import time
import re

from tweepy import Stream  # type: ignore
from mycollect.collectors import Collector
from mycollect.logger import create_logger
from mycollect.structures import MyCollectItem
from mycollect.utils import unshorten_url


class TwitterCollector(Stream, Collector):  # pylint:disable=too-many-instance-attributes
    """Twitter collector, based on Tweepy streaming
    """

    def __init__(self, consumer_key, consumer_secret,  # pylint:disable=too-many-arguments
                 access_token, access_secret, languages, low_priority_url, track):
        super().__init__(consumer_key=consumer_key, consumer_secret=consumer_secret,
                         access_token=access_token, access_token_secret=access_secret)
        self._logger = create_logger().bind(collector='twitter')
        self._languages = languages
        self._low_priority_url = low_priority_url
        self._last_data = time.time()
        self._timer_counter = 1
        self._track, self._filters = self.parse_track(track)
        self._exit = False

    def start(self):
        """Collect data from twitter
        """
        self._last_data = time.time()
        self.filter(
            track=self._track, languages=self._languages, threaded=True)

    def check_status(self):
        """Check the status of the collect
        """
        if not self.running and not self._exit:
            self._logger.info("twitter collect not running, restarting",
                              running=self.running)
            self.disconnect()
            self.start()
        elif time.time() - self._last_data > 1 * 60 * self._timer_counter and not self._exit:
            self._logger.info("twitter restart after being idle",
                              running=self.running,
                              timer_counter=self._timer_counter,
                              last_data=self._last_data)
            self.disconnect()
            self.start()
            if self._timer_counter < 60:
                self._timer_counter += 1

    def stop(self):
        """Stops the streaming
        """
        if not self._exit:
            self._exit = True
            self.disconnect()

    def on_data(self, raw_data):
        try:
            self._last_data = time.time()
            self._timer_counter = 1
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
                    self._logger.exception(err)
                    raise

            if url and category and not self.match_filter(category, loaded_tweet.get("text", "")):
                item = MyCollectItem(provider="twitter",
                                     category=category,
                                     text=loaded_tweet.get("text", None),
                                     url=url)
                item.extra["tweet"] = loaded_tweet
                self.emit(item)
        except BaseException as err:  # pylint:disable=broad-except
            self._logger.error(f"on_data unexpected error: {err}")
            self._logger.debug(err, exception=err)
        return True

    def on_request_error(self, status_code):
        self._logger.error("twitter error", status=status_code)
        return True

    def on_exception(self, exception):
        self._logger.error("twitter exception", exception=exception)

    def on_disconnect(self):
        self._logger.warn("twitter disconnection")

    def get_category(self, tweet: dict) -> Optional[str]:
        """Gets the category associated to the tweet

        Arguments:
            tweet {dict} -- tweet as dict

        Returns:
            str -- category of the tweet
        """
        best_track: Optional[Tuple[str, int]] = None
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
                elif best_track[1] < len(words):  # pylint: disable=unsubscriptable-object
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

    @ staticmethod
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

    @ staticmethod
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

    @ staticmethod
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

    def match_filter(self, category: str, text: str) -> bool:
        """Does the text match a filter of this category

        Args:
            category (str): the category of the tweet
            text (str): the text of the tweet

        Returns:
            bool: True if it matches a filter, False otherwise
        """
        lower_text = text.lower()
        for cat_filter in self._filters.get(category, []):
            if cat_filter in lower_text:
                return True
        return False

    @staticmethod
    def parse_track(track: List[str]) -> Tuple[List[str], Dict[str, List[str]]]:
        """Parse the tracks to find filters

        Args:
            track (List[str]): List of text that compose the track

        Returns:
            Tuple[List[str], Dict[str, List[str]]]: the new track and the filters
        """
        token_filter = re.compile(r"\s-([a-zA-Z]+)")
        group_filter: Dict[str, List[str]] = {}
        new_track = list(track)
        for idx, search in enumerate(new_track):
            updated_search = search
            local_filters = []
            tokens = list(token_filter.finditer(search))
            tokens.reverse()
            for match in tokens:
                local_filters.append(match.group(1).lower())
                updated_search = updated_search[0:match.start()] + \
                    updated_search[match.end():]
            new_track[idx] = updated_search
            group_filter[updated_search] = local_filters
        return new_track, group_filter
