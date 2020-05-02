"""Starter module for oracle
"""

import asyncio

import schedule
import yaml

from oracle.logger import configure, create_logger
from oracle.utils import get_class


async def main_loop():
    """This is the run forever loop definition
    """

    configuration = yaml.safe_load(open("config.yaml", "rb"))

    configure(configuration["logging"])
    logger = create_logger()

    collectors = {}

    for collector in configuration["collectors"]:
        collector_class = get_class(collector["type"])
        args = collector.get("args", {})
        collector_instance = collector_class(**args)
        collectors[collector["name"]] = collector_instance

    processors = {}
    for processor in configuration["processors"]:
        processor_class = get_class(processor["type"])
        args = processor.get("args", {})
        processor_instance = processor_class(**args)
        processors[processor["name"]] = processor_instance

    for collector in collectors:
        logger.info("starting collector", collector=collector)
        collectors[collector].collect()

    for processor in processors:
        schedule.every().day.at("02:00").do(processors[processor].process)

    try:
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        for local_collector in collectors:
            logger.info("stopping collector", collector=local_collector)
            collectors[local_collector].stop()
        logger.info("shutdown gracefully")

if __name__ == '__main__':
    asyncio.run(main_loop())
