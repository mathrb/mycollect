"""Outputs results into an email
"""

import boto3
from jinja2 import Template

from mycollect.logger import create_logger
from mycollect.outputs import Output


class EmailOutput(Output):
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

    def render(self, aggregate: dict) -> None:
        """Renders the aggregate as an email and send it

        Args:
            aggregate (dict): aggregate
        """
        body = self._template.render(results=aggregate)
        sent = self._client.send_email(
            Destination={"ToAddresses": self._recipients},
            Message={'Body': {'Html': {'Data': body, 'Charset': 'UTF-8'}},
                     'Subject': {'Data': 'News reporting', 'Charset': 'UTF-8'}},
            Source=self._sender)
        self._logger.info("email sent", result=sent)

    def set_auth(self, aws_access_key, aws_secret_key, aws_region):
        """Set aws authentication
        """
        self._client = boto3.client(
            'ses',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key)
