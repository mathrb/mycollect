"""Outputs results into an email
"""
from collections import defaultdict
from typing import List

import boto3
from jinja2 import Template

from mycollect.logger import create_logger
from mycollect.structures import MyCollectItem


class EmailOutput():
    """Send results to email recipients
    """

    def __init__(self, aws_access_key, aws_secret_key, aws_region,  # pylint:disable=too-many-arguments
                 template, recipients, sender, limit_per_category=3):
        if aws_region:
            self.set_auth(aws_access_key, aws_secret_key, aws_region)
        else:
            self._client = None
        self._recipients = recipients
        self._template = Template(template)
        self._sender = sender
        self._limit_per_category = limit_per_category
        self._logger = create_logger()

    def output(self, results: List[MyCollectItem]):
        """Send the results through email

        Arguments:
            results {list} -- data results
        """
        body = self.generate_body(results)
        sent = self._client.send_email(
            Destination={"ToAddresses": self._recipients},
            Message={'Body': {'Html': {'Data': body, 'Charset': 'UTF-8'}},
                     'Subject': {'Data': 'News reporting', 'Charset': 'UTF-8'}},
            Source=self._sender)
        self._logger.info("email sent", result=sent)

    def generate_body(self, results):
        """Generates body from results and template

        Arguments:
            results {list} -- data results

        Returns:
            str -- body
        """
        categories = defaultdict(dict)
        for mycollect_item in results:
            if mycollect_item.url not in categories[mycollect_item.category]:
                categories[mycollect_item.category][mycollect_item.url] = []
            categories[mycollect_item.category][mycollect_item.url].append(
                mycollect_item)
        results = {}
        for category, url_dict in sorted(categories.items()):
            category_items = []
            for url, mycollect_items in url_dict.items():
                item = {
                    "url": url,
                    "count": len(mycollect_items),
                    "text": mycollect_items[0].text
                }
                category_items.append(item)
            items = sorted(
                category_items, key=lambda x: x["count"], reverse=True)
            results[category] = items[:self._limit_per_category]
        return self._template.render(results=results)

    def set_auth(self, aws_access_key, aws_secret_key, aws_region):
        """Set aws authentication
        """
        self._client = boto3.client(
            'ses',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key)
