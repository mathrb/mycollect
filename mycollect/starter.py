"""Starter module for mycollect
"""

import asyncio
from typing import List

import schedule
import yaml

from mycollect.logger import configure, create_logger
from mycollect.utils import get_class
from mycollect.collectors import Collector


def load_types(items):
    """Loads the types defined in configuration section

    Arguments:
        items {list} -- list of types defined in configuration

    Returns:
        dict -- key: name, value: instance
    """
    collection = {}
    for item in items:
        item_class = get_class(item["type"])
        args = item.get("args", {})
        item_instance = item_class(**args)
        collection[item["name"]] = item_instance
    return collection


def execute_processing(processor, outputs):
    """Starts processing the data

    Arguments:
        processor {processor} -- processor
        outputs {list} -- list of output instances
    """
    result = processor.process()
    for output in outputs:
        outputs[output].output(result)


async def main_loop():
    """This is the run forever loop definition
    """

    configuration = yaml.safe_load(open("config.yaml", "rb"))

    configure(configuration["logging"])
    logger = create_logger()

    collectors: List[Collector] = load_types(configuration["collectors"])
    processors = load_types(configuration["processors"])
    outputs = load_types(configuration["outputs"])

    for collector in collectors:
        logger.info("starting collector", collector=collector)
        collectors[collector].start()

    execution_time = "02:00"
    processing = configuration.get("processing", None)
    if processing:
        execution_time = processing.get("execution_time", "02:00")

    for processor in processors:
        schedule.every().day.at(execution_time).do(
            execute_processing, processors[processor], outputs)

    try:
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)
            for local_connector in collectors:
                collectors[local_connector].check_status()
    except KeyboardInterrupt:
        for local_collector in collectors:
            logger.info("stopping collector", collector=local_collector)
            collectors[local_collector].stop()
        logger.info("shutdown gracefully")

if __name__ == '__main__':
    asyncio.run(main_loop())
