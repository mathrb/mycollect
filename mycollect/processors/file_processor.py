"""Process an input file
"""
import datetime
import json
import os

from mycollect.storage import Storage
from mycollect.logger import create_logger
from mycollect.structures import MyCollectItem


class FileProcessor():
    """Process a file and execute action
    """

    def __init__(self, data_manager: Storage):
        self._offset_file = ".file_processor_offset"
        self._logger = create_logger()
        self._data_manager = data_manager

    def process(self):
        """Process the file and take actions
        """
        mycollect_items = []
        last_offset = self.get_offset()
        current_offset = round(datetime.datetime.now().timestamp())
        for tweet in self._data_manager.fetch_items(last_offset):
            try:
                category = tweet.get("_category")
                url = tweet.get("_url")
                if category and url:
                    mycollect_items.append(MyCollectItem(
                        category=category, text=tweet.get("text", None), url=url))
                else:
                    print(tweet["id"])
            except json.decoder.JSONDecodeError:
                pass
        self.set_offset(current_offset)
        return mycollect_items

    def get_offset(self):
        """Get last offset

        Returns:
            int -- offset
        """
        if os.path.exists(self._offset_file):
            try:
                with open(self._offset_file) as file_input:
                    return int(file_input.readline().strip())
            except Exception as err:  # pylint:disable=broad-except
                self._logger.exception(err)
        return 0

    def set_offset(self, offset):
        """Writes the offset to the file

        Arguments:
            offset {int} -- offset
        """
        with open(self._offset_file, "w") as file_output:
            file_output.write(str(offset))
