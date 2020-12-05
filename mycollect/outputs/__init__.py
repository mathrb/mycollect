"""Outputs gets aggregates and render them
"""

import abc


class Output(metaclass=abc.ABCMeta):  # pylint:disable=R0903
    """Output class that renders an aggregate
    """

    def render(self, aggregate: dict, notification_channel: str = None) -> None:
        """Render the aggregate

        Args:
            aggregate (dict): the aggregate
            notification_channel (str): the notification channel used by the aggregator
        """
