"""Outputs results into an email
"""
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3 # type: ignore
from jinja2 import Template
from mycollect.logger import create_logger
from mycollect.outputs import Output


class AWSSender():  # pylint:disable=too-few-public-methods

    """Send emails using AWS
    """

    def __init__(self, aws_access_key, aws_secret_key, aws_region, **kwargs):
        self._kwargs = kwargs
        self._client = boto3.client(
            'ses',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key)

    def send_email(self, sender, recipients, subject, body):
        """Send an email to the specified recipients

        Args:
            sender (str): email address that sends the email
            recipients (List[str]): list of recipients email addresses
            subject (str): subject
            body (str): body

        Returns:
            Any: Service response
        """
        return self._client.send_email(
            Destination={"ToAddresses": recipients},
            Message={'Body': {'Html': {'Data': body, 'Charset': 'UTF-8'}},
                     'Subject': {'Data': subject, 'Charset': 'UTF-8'}},
            Source=sender)


class SMTPSender():

    """Send an email using SMTP server
    """

    def __init__(self, host, port=25, **kwargs):
        self._host = host
        self._port = port
        self._kwargs = kwargs

    def send_email(self, sender, recipients, subject, body):
        """Send an email to the specified recipients

        Args:
            sender (str): email address that sends the email
            recipients (List[str]): list of recipients email addresses
            subject (str): subject
            body (str): body

        Returns:
            Any: Service response
        """
        smtp_client = smtplib.SMTP()
        smtp_client.connect(host=self._host, port=self._port)
        message = self.create_message(sender, recipients, subject, body)
        return smtp_client.sendmail(message["From"], message["To"], message.as_string())

    @staticmethod
    def create_message(sender, recipients, subject, body):
        """Creates the MIMEMultipart message

        Args:
            sender (str): email address that sends the email
            recipients (List[str]): list of recipients email addresses
            subject (str): subject
            body (str): body
        """
        message = MIMEMultipart("alternative")
        message['Subject'] = Header(subject, "utf-8")
        message['From'] = sender
        message['To'] = ", ".join(recipients)
        html = MIMEText(body, "html", "utf-8")
        message.attach(html)
        return message


class EmailOutput(Output):  # pylint:disable=too-few-public-methods
    """Send results to email recipients
    """

    def __init__(self, recipients, sender, templates, **kwargs):
        self._email_sender = None
        if "aws" in kwargs:
            self._email_sender = AWSSender(**kwargs["aws"])
        elif "smtp" in kwargs:
            self._email_sender = SMTPSender(**kwargs["smtp"])
        else:
            raise ValueError(
                "Email output must have smtp or aws config to send emails")
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
                sent = self._email_sender.send_email(
                    self._sender, self._recipients, "News reporting", body)
                self._logger.info("email sent", result=sent,
                                  notification_channel=notification_channel)


if __name__ == "__main__":
    email_sender = SMTPSender("192.168.0.21")
    print(email_sender.send_email("MyCollect <mycollect@mathrb.com>",
                                  ["mathrb@gmail.com"], "News reporting", "Coucou"))
