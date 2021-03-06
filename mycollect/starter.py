"""Starter module for mycollect
"""

import argparse
import datetime
import time
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore
import yaml

from mycollect.aggregators import Aggregator
from mycollect.collectors import Collector
from mycollect.logger import configure_logger, create_logger
from mycollect.outputs import Output
from mycollect.processors import PipelineProcessor
from mycollect.processors.exit_processor import ExitProcessor
from mycollect.storage import Storage
from mycollect.utils import get_class, get_object_fqdn

SCHEDULER = BackgroundScheduler()


def load_types(items, extra_args: dict = None, return_config=False):
    """Loads the types defined in configuration section

    Arguments:
        items {list} -- list of types defined in configuration

    Returns:
        dict -- key: name, value: instance
    """
    collection = {}
    for item in items:
        collection[item["name"]] = load_type(item, extra_args=extra_args)
        if return_config:
            collection[item["name"]] = {
                "instance": collection[item["name"]],
                "configuration": item
            }
    return collection


def load_type(item, extra_args: dict = None):
    """Loads the specified item defined by configuration

    Args:
        item (dict): configuration e
        extra_args (dict, optional): extra arguments for the instanciation.
            Defaults to None.

    Returns:
        [type]: An instance of type defined in the item
    """
    item_class = get_class(item["type"])
    args = item.get("args", {})
    if extra_args:
        args.update(extra_args)
    return item_class(**args)


def run_aggregator(storage: Storage, aggregator: Aggregator, outputs: List[Output], logger):
    """Runs the aggregator and notify the outputs

    Args:
        storage (Storage): storage reference
        aggregator (Aggregator): aggregator that needs to run
        outputs (List[Output]): outputs
    """
    local_logger = logger.bind(agg_type=get_object_fqdn(aggregator))
    local_logger = local_logger.bind(notification_channel=aggregator.notify)
    local_logger = local_logger.bind(outputs=len(outputs))
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    timestamp = round(yesterday.timestamp())
    local_logger.info("aggregator run started", from_timestamp=timestamp)
    agg = aggregator.aggregates(storage.fetch_items(timestamp))
    for output in outputs:
        output.render(agg, aggregator.notify)
    local_logger.info("aggregator run ended")
    log_next_runs()


def log_next_runs():
    """Logs the next jobs to run
    """
    logger = create_logger()
    for job in SCHEDULER.get_jobs():
        logger = logger.bind(
            job_name=job.name, next_run=job.next_run_time.isoformat())
        if len(job.args) > 1 and isinstance(job.args[1], Aggregator):
            logger = logger.bind(agg_name=get_object_fqdn(job.args[1]))
        logger.info("next job scheduled")


def main_loop(config, infinite=True):  # pylint:disable=too-many-locals
    """This is the run forever loop definition
    """

    configuration = yaml.safe_load(open(config, "rb"))
    configure_logger(configuration["logging"])
    logger = create_logger()
    collectors: List[Collector] = load_types(configuration["collectors"])
    storages: List[Storage] = load_types(
        configuration["storages"], return_config=True)
    storage: Storage = [
        s for s in storages if storages[s]["configuration"].get("default", False)]
    if not storage:
        raise Exception(
            "A default storage needs to be set. Add a default property to one of the storage")
    storage = storage[0]
    processors = load_types(
        configuration["processors"]) if "processors" in configuration else []
    aggregators = load_types(configuration["aggregators"])
    outputs = load_types(configuration["outputs"])

    pipeline = PipelineProcessor()
    for processor in processors:
        pipeline.append_processor(processors[processor])
    pipeline.append_processor(ExitProcessor([storages[s]["instance"] for s in storages]))

    for collector in collectors:
        logger.info("starting collector", collector=collector)
        collectors[collector].set_callback(pipeline.update_item)
        collectors[collector].start()

    for aggregator in aggregators:
        run_agg_args = [storage, aggregators[aggregator],
                        outputs.values(), logger]
        trigger = CronTrigger.from_crontab(aggregators[aggregator].schedule)
        SCHEDULER.add_job(run_aggregator, trigger, args=run_agg_args)

    SCHEDULER.start()
    log_next_runs()
    try:
        while infinite:
            time.sleep(1)
            for local_connector in collectors:
                collectors[local_connector].check_status()
    except KeyboardInterrupt:
        for local_collector in collectors:
            logger.info("stopping collector", collector=local_collector)
            collectors[local_collector].stop()
        SCHEDULER.shutdown()
        logger.info("shutdown gracefully")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configuration",
                        help="path to configuration file", default="config.yaml")
    sys_args = parser.parse_args()
    main_loop(config=sys_args.configuration)
