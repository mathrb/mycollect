"""
    File storage stores data into files
    One folder per provider, one file per day
"""
import datetime
import json
import os

from mycollect.storage import Storage
from mycollect.structures import MyCollectItem
from mycollect.logger import create_logger


class FileStorage(Storage):
    """
        FileStorage class
        One folder per provider, one file per day
    """

    def __init__(self, folder: str):
        os.makedirs(folder, exist_ok=True)
        self._folder = folder
        self._logger = create_logger()

    def store_item(self, item: MyCollectItem) -> None:
        if not item.provider:
            self._logger.warning("empty provider")
            return
        provider = item.provider
        provider_path = os.path.join(self._folder, provider)
        if not os.path.exists(provider_path):
            os.makedirs(provider_path)
        timestamp = round(datetime.datetime.now().timestamp())
        file_path = self._get_file_path(provider, timestamp)
        with open(file_path, 'a', encoding='utf-8') as output_file:
            item_to_dump = {
                "timestamp": timestamp,
                "data": item.to_dict()
            }
            output_file.write(json.dumps(item_to_dump) + '\n')

    def fetch_items(self, timestamp: int):
        for provider in os.listdir(self._folder):
            current_date = datetime.datetime.fromtimestamp(timestamp)
            while current_date.date() <= datetime.datetime.now().date():
                file_path = self._get_file_path(
                    provider, round(current_date.timestamp()))
                if os.path.exists(file_path):
                    with open(file_path, encoding='utf-8') as input_file:
                        for line in input_file:
                            try:
                                item = json.loads(line)
                                if item["timestamp"] >= timestamp:
                                    yield MyCollectItem.from_dict(item["data"])
                            except json.decoder.JSONDecodeError:
                                self._logger.warn(f"Invalid json line in file {file_path}: {line}")
                current_date += datetime.timedelta(days=1)

    def _get_file_path(self, provider, timestamp: int):
        provider_path = os.path.join(self._folder, provider)
        date = datetime.datetime.fromtimestamp(timestamp)
        file_name = date.strftime("%Y_%m_%d.jsonl")
        return os.path.join(provider_path, file_name)
