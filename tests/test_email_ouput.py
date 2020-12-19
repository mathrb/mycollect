"""Tests the email output
"""

import pytest

from mycollect.outputs.email_output import EmailOutput
from mycollect.structures import MyCollectItem


def test_email_output():
    with pytest.raises(ValueError):
        _ = EmailOutput(["john.doe@gmail.com"], "mycollect@gmail.com", [])
    _ = EmailOutput(["john.doe@gmail.com"], "mycollect@gmail.com", [],
                    aws={"aws_access_key": "", "aws_secret_key": "", "aws_region": "eu-west-1"})
    _ = EmailOutput(["john.doe@gmail.com"],
                    "mycollect@gmail.com", [], smtp={"host": "localhost"})


def test_generate_body():
    # content = "".join(open("tests/test_files/email_template.j2"))
    # email_output = EmailOutput(None, None, None, content, None, None, 3)
    # assert email_output.render([])
    # items = []
    # items.append(MyCollectItem("prov", "foo", "my text 1", "http://google.com"))
    # items.append(MyCollectItem("prov", "foo", "my text 2", "http://google.com"))
    # items.append(MyCollectItem("prov", "foo", "my text 3", "http://google.com"))
    # items.append(MyCollectItem("prov", "bar", "my text 1", "http://google.fr"))
    # items.append(MyCollectItem("prov", "bar", "my text 2", "http://google.fr"))
    # items.append(MyCollectItem("prov", "bar", "my text 3", "http://google.fr"))
    # body = email_output.render(items)
    # assert body
    # assert body == "".join(open("tests/test_files/email_result_1.html"))
    # items.append(MyCollectItem("prov", "bar", "my text 4", "http://google.fr"))
    # body = email_output.render(items)
    # assert body != "".join(open("tests/test_files/email_result_1.html"))
    # assert body == "".join(open("tests/test_files/email_result_2.html"))
    # items.append(MyCollectItem("prov", "bar", "my text 5", "http://google.it"))
    # items.append(MyCollectItem("prov", "bar", "my text 6", "http://google.de"))
    # items.append(MyCollectItem("prov", "bar", "my text 7", "http://google.es"))
    # body = email_output.render(items)
    # assert body == "".join(open("tests/test_files/email_result_3.html"))
    pass
