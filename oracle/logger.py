"""
    Logger helper
"""
from typing import Dict
import logging.config

import structlog  # type: ignore

from oracle import __version__


TIMESTAMPER = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")


def plain_colored_formatter():
    """Defines the plain colored formatter

    Returns:
        Formatter -- the formatter used to format logs for the console
    """
    return structlog.stdlib.ProcessorFormatter(processor=structlog.dev.ConsoleRenderer(colors=True))


def create_logger() -> structlog.BoundLogger:
    """Creates the technical logger

    Returns:
        BoundLogger -- structlog logger
    """
    return _bind_basic_info(structlog.get_logger("oracle"))

def _bind_basic_info(logger):
    return logger.bind(version=__version__)

def configure(configuration: Dict) -> None:
    """Configure the logging library based on the configuration

    Arguments:
        configuration {Configuration} -- Configuration
    """
    logging.config.dictConfig(configuration)
    structlog.configure(
        processors=[structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    TIMESTAMPER,
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
