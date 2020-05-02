import schedule
import yaml
import asyncio

from oracle.logger import create_logger, configure
from oracle.utils import get_class

configuration = yaml.safe_load(open("config.yaml", "rb"))

configure(configuration["logging"])
LOGGER = create_logger()

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
    LOGGER.info("starting collector", collector=collector)
    collectors[collector].collect()

for processor in processors:
    schedule.every().day.at("02:00").do(processors[processor].process)

async def main_loop():
    try:
        while True:        
            schedule.run_pending()
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        for collector in collectors:
            LOGGER.info("stopping collector", collector=collector)
            collectors[collector].stop()
        LOGGER.info("shutdown gracefully")

if __name__ == '__main__':
    asyncio.run(main_loop())