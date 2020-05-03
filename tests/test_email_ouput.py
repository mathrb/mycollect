"""Tests the email output
"""

from oracle.outputs.email_output import EmailOutput
from oracle.structures import OracleItem

def test_generate_body():
    content = "".join(open("tests/test_files/email_template.j2"))
    email_output = EmailOutput(None, None, None, content, None, None, 3)
    assert email_output.generate_body([])
    items = []
    items.append(OracleItem("foo", "my text 1", "http://google.com"))
    items.append(OracleItem("foo", "my text 2", "http://google.com"))
    items.append(OracleItem("foo", "my text 3", "http://google.com"))
    items.append(OracleItem("bar", "my text 1", "http://google.fr"))
    items.append(OracleItem("bar", "my text 2", "http://google.fr"))
    items.append(OracleItem("bar", "my text 3", "http://google.fr"))
    body = email_output.generate_body(items)
    assert body
    assert body == "".join(open("tests/test_files/email_result_1.html"))
    items.append(OracleItem("bar", "my text 4", "http://google.fr"))
    body = email_output.generate_body(items)
    assert body != "".join(open("tests/test_files/email_result_1.html"))
    assert body == "".join(open("tests/test_files/email_result_2.html"))
    items.append(OracleItem("bar", "my text 5", "http://google.it"))
    items.append(OracleItem("bar", "my text 6", "http://google.de"))
    items.append(OracleItem("bar", "my text 7", "http://google.es"))
    body = email_output.generate_body(items)
    assert body == "".join(open("tests/test_files/email_result_3.html"))
