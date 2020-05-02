from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
from urllib.parse import urlparse
import json

from oracle.logger import create_logger

class TwitterCollector(StreamListener):

    def __init__(self, output_file, consumer_key, consumer_secret, access_token, access_secret, low_priority_url, track):
        self._logger = create_logger().bind(collector='twitter')
        self._track = track
        self._low_priority_url = low_priority_url
        self._output_file = output_file
        self._auth = OAuthHandler(consumer_key, consumer_secret)
        self._auth.set_access_token(access_token, access_secret)

    def collect(self):
        self._twitter_stream = Stream(self._auth, self)
        self._twitter_stream.filter(track=self._track, is_async=True)

    def stop(self):
        self._twitter_stream.disconnect()

    def on_data(self, data):
        try:
            loaded_tweet = json.loads(data)
            category = self.get_category(loaded_tweet)
            if category is not None:
                loaded_tweet["_category"] = category
            rt = loaded_tweet.get("retweeted_status", None)
            if rt is not None:                        
                url = self.get_url_from_tweet(loaded_tweet["retweeted_status"])
                if not url:
                    url = self.get_url_from_tweet(loaded_tweet)
            else:
                url = self.get_url_from_tweet(loaded_tweet)
            loaded_tweet["_url"] = url
            with open(self._output_file, 'a') as f:
                f.write(json.dumps(loaded_tweet) + "\n")
        except BaseException as e:
            self._logger.error("on_data unexpected error: {}".format(e))
            self._logger.exception(e)
        return True
 
    def on_error(self, status):
        self._logger.error("twitter error", status=status)
        return True

    def get_category(self, tweet):
        best_track = None
        full_text = self.get_track_text(tweet).lower()
        for track in self._track:
            words = track.split()
            i=len(words)
            for w in words:
                if w in full_text:
                    i-=1
            if i == 0:
                if best_track is None:
                    best_track = (track, len(words))
                elif best_track[1] < len(words):
                    best_track = (track, len(words))
        if best_track:
            return best_track[0]
        return None

    def get_url_from_tweet(self, tweet):
        real_url = None
        if "entities" in tweet:
            for url in TwitterCollector.get_expanded_urls_in_entities(tweet["entities"]):
                o = urlparse(url)
                if real_url is None:
                    real_url = o
                if real_url.netloc in self._low_priority_url and o.netloc not in self._low_priority_url:
                    real_url = o
        return real_url.geturl() if real_url else None 

    @staticmethod
    def get_track_text(tweet):
        if "text" in tweet:
            text = tweet["text"]
        else:
            text = ''
        if "extended_tweet" in tweet and "full_text" in tweet["extended_tweet"]:
            text = tweet["extended_tweet"]["full_text"]
            if 'entities' in tweet["extended_tweet"]:
                text += TwitterCollector.get_text_of_urls_entities(tweet["extended_tweet"]["entities"])
        if 'entities' in tweet:
            text += TwitterCollector.get_text_of_urls_entities(tweet["entities"])
        if 'quoted_status' in tweet:
            if 'extended_tweet' in tweet["quoted_status"]:
                text += ' ' + tweet["quoted_status"]["extended_tweet"]["full_text"]
                if "entities" in tweet["quoted_status"]["extended_tweet"]:
                    text += TwitterCollector.get_text_of_urls_entities(tweet["quoted_status"]["extended_tweet"])
            else:
                text += ' ' + tweet["quoted_status"]["text"]
        if "retweeted_status"  in tweet:
            return TwitterCollector.get_track_text(tweet["retweeted_status"])
        return text

    @staticmethod
    def get_text_of_urls_entities(item: dict):
        text=''
        for url in TwitterCollector.get_urls_in_entities(item):
            if 'expanded_url' in url:
                text += ' ' + url['expanded_url']
            if 'display_url' in url:
                text += ' ' + url['display_url']
        return text

    @staticmethod
    def get_expanded_urls_in_entities(item: dict):
        for url in TwitterCollector.get_urls_in_entities(item):
            yield url["expanded_url"]

    @staticmethod
    def get_urls_in_entities(item: dict):
        if "urls" in item:
            for url in item["urls"]:
                yield url

    __call__ = collect
