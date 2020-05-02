from collections import defaultdict
import json
import os

import boto3
from botocore.exceptions import ClientError

from oracle.logger import create_logger

class FileProcessor():

    def __init__(self, input_file, aws_access_key, aws_secret_key):
        self._input_file = input_file
        self._ses_data = {
            "sender": "Collect <mathrb@gmail.com>",
            "recipient": "mathrb@gmail.com",
            "aws_region": "us-west-2",
            "aws_access_key": aws_access_key,
            "aws_secret_key": aws_secret_key
        }
        self._offset_file = ".file_processor_offset"
        self._logger = create_logger()

    def process(self):
        cats = defaultdict(dict)
        last_offset = self.get_offset()
        current_offset = 0
        for line in open(self._input_file):
            current_offset +=1
            if line.strip() != '' and current_offset > last_offset:
                try:
                    tweet = json.loads(line)
                    category = tweet.get("_category")
                    url = tweet.get("_url")            
                    if category and url:
                        if url not in cats[category]:
                            cats[category][url] = []
                        cats[category][url].append({
                            "url": url,
                            "category": category,
                            "text": tweet.get("text", None)
                        })
                except json.decoder.JSONDecodeError:
                    pass
        if cats:            
            body = self.generate_body_email(cats)
        else:
            body = "Nothing new"
        client = boto3.client('ses',region_name=self._ses_data["aws_region"], aws_access_key_id=self._ses_data["aws_access_key"],aws_secret_access_key=self._ses_data["aws_secret_key"])
        sent = client.send_email(
            Destination={"ToAddresses":[self._ses_data["recipient"]]}, 
            Message={'Body': {'Html': {'Data': body, 'Charset': 'UTF-8'}}, 'Subject':{'Data': 'News reporting', 'Charset': 'UTF-8'}}, 
            Source=self._ses_data["sender"])
        self._logger.info("email sent", elements=len(cats), result=sent)
        self.set_offset(current_offset -1)

    def generate_body_email(self, cats):
        body = """<html>
            <head></head>
            <body>
            <h1>News Reporting</h1>
            {}
            </body>
            </html>
        """
        html_elements = []
        for cat in cats:
            urls = sorted(cats[cat], key=lambda x: len(cats[cat][x]), reverse=True)
            if urls:
                html_element = "<h2>{}</h2>".format(cat)
                for url in urls[:3]:
                    clear_tweet = cats[cat][url][0]
                    html_element += "<p>({}) {}<br><a href='{}'>{}</a></p>".format(len(cats[cat][url]), clear_tweet["text"], clear_tweet["url"], clear_tweet["url"])
                html_elements.append(html_element)
        body = body.format('<br>'.join(html_elements))
        return body    

    def get_offset(self):
        if os.path.exists(self._offset_file):
            try:
                with open(self._offset_file) as fi:
                    return int(fi.readline().strip())
            except Exception as err:
                self._logger.exception(err)
        return 0

    def set_offset(self, offset):
        with open(self._offset_file, "w") as fo:
            fo.write(str(offset))

if __name__ == "__main__":
    import yaml
    configuration = yaml.safe_load(open("config.yaml", "rb"))
    for processor in configuration["processors"]:
        if processor["name"] == "file":
            fp = FileProcessor(**processor["args"])
            fp.process()