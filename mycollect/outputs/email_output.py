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
                 recipients, sender, templates):
        if aws_region:
            self.set_auth(aws_access_key, aws_secret_key, aws_region)
        else:
            self._client = None
        self._recipients = recipients
        self._templates = {}
        for template in templates:
            self._templates[template["name"]] = Template(template["template"])
        self._sender = sender
        self._logger = create_logger()

    def render(self, aggregate: dict, notification_channel: str = None) -> None:
        """Renders the aggregate as an email and send it

        Args:
            aggregate (dict): aggregate
            notification_channel (str): the notification channel used by the aggregator
        """
        for template in self._templates:
            if template == notification_channel:
                body = self._templates[template].render(results=aggregate)
                sent = self._client.send_email(
                    Destination={"ToAddresses": self._recipients},
                    Message={'Body': {'Html': {'Data': body, 'Charset': 'UTF-8'}},
                             'Subject': {'Data': 'News reporting', 'Charset': 'UTF-8'}},
                    Source=self._sender)
                self._logger.info("email sent", result=sent,
                                  notification_channel=notification_channel)

    def set_auth(self, aws_access_key, aws_secret_key, aws_region):
        """Set aws authentication
        """
        self._client = boto3.client(
            'ses',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key)
