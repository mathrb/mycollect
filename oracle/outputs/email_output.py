"""Outputs results into an email
"""
from collections import defaultdict
from typing import List

import boto3
from jinja2 import Template

from oracle.logger import create_logger
from oracle.structures import OracleItem


class EmailOutput():
    """Send results to email recipients
    """

    def __init__(self, aws_access_key, aws_secret_key, aws_region,
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

    def output(self, results: List[OracleItem]):
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
        for oracle_item in results:
            if oracle_item.url not in categories[oracle_item.category]:
                categories[oracle_item.category][oracle_item.url] = []
            categories[oracle_item.category][oracle_item.url].append(
                oracle_item)
        results = {}
        for category, url_dict in categories.items():
            category_items = []
            for url, items in url_dict.items():
                item = {
                    "url": url,
                    "count": len(items),
                    "text": items[0].text
                }
                category_items.append(item)
            items = sorted(category_items, key=lambda x: x["count"], reverse=True)
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

if __name__ == "__main__":    
    import yaml
    CONFIGURATION = yaml.safe_load(open("config.yaml", "rb"))
    for processor in CONFIGURATION["outputs"]:
        if processor["name"] == "email":
            email = EmailOutput(**processor["args"])
            items = []
            items.append(OracleItem("foo", "my text 1", "http://google.com"))
            items.append(OracleItem("foo", "my text 2", "http://google.com"))
            items.append(OracleItem("foo", "my text 3", "http://google.com"))
            items.append(OracleItem("bar", "my text 1", "http://google.fr"))
            items.append(OracleItem("bar", "my text 2", "http://google.fr"))
            items.append(OracleItem("bar", "my text 3", "http://google.fr"))
            email.output(items)