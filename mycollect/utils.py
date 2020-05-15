"""Utils for mycollect
"""


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
