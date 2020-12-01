"""Starter module for mycollect
"""

import asyncio
from typing import List
import datetime

import schedule
import yaml

from mycollect.logger import configure_logger, create_logger
from mycollect.utils import get_class
from mycollect.collectors import Collector
from mycollect.storage import Storage
from mycollect.processors import PipelineProcessor
from mycollect.processors.exit_processor import ExitProcessor
from mycollect.aggregators import Aggregator
from mycollect.outputs import Output


def load_types(items, extra_args: dict = None):
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
        if extra_args:
            args.update(extra_args)
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

def report(storage: Storage, aggregators: List[Aggregator], outputs: List[Output]):
    """Report

    Args:
        storage (Storage): storage
        aggregators (List[Aggregator]): aggregators
        outputs (List[Output]): outputs
    """
    timestamp = round(datetime.datetime.now().timestamp())
    aggregates = []
    for aggregator in aggregators:
        aggregates.append(aggregator.aggregates(storage.fetch_items(timestamp)))
    for output in outputs:
        for agg in aggregates:
            output.render(agg)

async def main_loop():
    """This is the run forever loop definition
    """

    configuration = yaml.safe_load(open("config.yaml", "rb"))

    configure_logger(configuration["logging"])
    logger = create_logger()

    collectors: List[Collector] = load_types(configuration["collectors"])
    storage: Storage = load_types([configuration["storage"]]).pop()
    processors = load_types(configuration["processors"])
    aggregators = load_types(configuration["aggregators"])
    outputs = load_types(configuration["outputs"])

    pipeline = PipelineProcessor()
    for processor in processors:
        pipeline.append_processor(processor)
    pipeline.append_processor(ExitProcessor(storage))

    for collector in collectors:
        logger.info("starting collector", collector=collector)
        collectors[collector].set_callback(pipeline.update_item)
        collectors[collector].start()

    execution_time = "02:00"
    processing = configuration.get("processing", None)
    if processing:
        execution_time = processing.get("execution_time", "02:00")

    for processor in processors:
        schedule.every().day.at(execution_time).do(
            report, storage, aggregators.values(), outputs.values())

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
