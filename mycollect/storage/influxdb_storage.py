"""Influx db storage
This storage is write only
"""
import socket

from influxdb.client import InfluxDBClient, InfluxDBClientError  # type: ignore

from mycollect.storage import Storage
from mycollect.structures import MyCollectItem
from mycollect.logger import create_logger


class InfluxDBStorage(Storage):

    """InfluxDB store only storage
    """

    def __init__(self, **kwargs):
        self._logger = create_logger()
        self._hostname = socket.gethostname()
        self._client = InfluxDBClient(
            kwargs["host"],
            kwargs["port"],
            kwargs["username"],
            kwargs["password"],
            kwargs["database"])
        try:
            self._client.create_database(kwargs["database"])
        except InfluxDBClientError as err:
            self._logger.exception(err)
        retention = kwargs.get("retention", "30d")
        try:
            self._client.create_retention_policy(
                "mycollect_retention_policy",
                retention,
                replication=1,
                database=kwargs["database"],
                default=True)
        except InfluxDBClientError as err:
            self._logger.exception(err)

    def store_item(self, item: MyCollectItem) -> None:
        fields = item.to_dict()
        fields.pop("extra", None)
        self._client.write_points([
            {
                "measurement": "mycollect_item",
                "tags": {
                    "host": self._hostname
                },
                # "time": datetime.datetime.now(),
                "fields": fields
            }]
        )
