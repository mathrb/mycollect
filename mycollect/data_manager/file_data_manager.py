"""
    File data manager stores data into files
    One folder per provider, one file per day
"""
import datetime
import json
import os
from typing import Any

from mycollect.data_manager import DataManager


class FileDataManager(DataManager):
    """
        FileDataManager class
        One folder per provider, one file per day
    """

    def __init__(self, folder: str):
        os.makedirs(folder, exist_ok=True)
        self._folder = folder

    def store_raw_data(self, provider: str, data: Any) -> None:
        provider_path = os.path.join(self._folder, provider)
        if not os.path.exists(provider_path):
            os.makedirs(provider_path)
        timestamp = round(datetime.datetime.now().timestamp())
        file_path = self._get_file_path(provider, timestamp)
        with open(file_path, 'a', encoding='utf-8') as output_file:
            item = {
                "timestamp" : timestamp,
                "data": data
            }
            output_file.write(json.dumps(item) + '\n')

    def read_raw_data(self, provider: str, timestamp: int):
        provider_path = os.path.join(self._folder, provider)
        if os.path.exists(provider_path):
            current_date = datetime.datetime.fromtimestamp(timestamp)
            while current_date.date() <= datetime.datetime.now().date():
                file_path = self._get_file_path(provider, round(current_date.timestamp()))
                if os.path.exists(file_path):
                    for line in open(file_path, encoding='utf-8'):
                        item = json.loads(line)
                        if item["timestamp"] >= timestamp:
                            yield item["data"]
                current_date += datetime.timedelta(days=1)

    def _get_file_path(self, provider, timestamp: int):
        provider_path = os.path.join(self._folder, provider)
        date = datetime.datetime.fromtimestamp(timestamp)
        file_name = date.strftime("%Y_%m_%d.jsonl")
        return os.path.join(provider_path, file_name)
