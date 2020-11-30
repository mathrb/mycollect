import pytest
from mycollect.utils import unshorten_url

@pytest.mark.parametrize("short_url,expected", [
    ("https://t.co/B1Ssk0L1Ne", "https://twitter.com/i/web/status/1255890125680246785"),
    ("https://msft.it/6010Tg0qC", "https://www.youtube.com/watch?v=uQ5BZht9L3A")])
def test_unshorten(short_url, expected):
    assert unshorten_url(short_url) == expected