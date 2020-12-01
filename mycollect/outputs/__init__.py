"""Outputs gets aggregates and render them
"""

import abc


class Output(metaclass=abc.ABCMeta): #pylint:disable=R0903
    """Output class that renders an aggregate
    """

    def render(self, aggregate: dict) -> None:
        """Render the aggregate

        Args:
            aggregate (dict): the aggregate
        """
