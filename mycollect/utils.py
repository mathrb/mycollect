"""Utils for mycollect
"""
import requests

def get_class(kls):
    """
    from string, returns the correspondent class
    :param kls:
    :return:
    """
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    module = __import__(module)
    for comp in parts[1:]:
        module = getattr(module, comp)
    return module

def unshorten_url(url):
    """
        Unshorten the url
    """
    response = requests.get(url, timeout=30)
    new_url = url
    for item in response.history:
        if item.status_code == 301 and "location" in item.headers:
            new_url = item.headers["location"]
    return new_url

def get_object_fqdn(obj):
    """Gets the fullname of the object

    Args:
        obj (Any): an object

    Returns:
        str: the fullname of the object
    """
    if hasattr(obj, "__module__"):
        return obj.__module__ + "." + obj.__class__.__qualname__
    return obj.__class__.__qualname__
