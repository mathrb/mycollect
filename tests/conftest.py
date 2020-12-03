import json

import pytest

from mycollect.structures import MyCollectItem


@pytest.fixture
def load_mycollect_items(request):
    marker = request.node.get_closest_marker("file")
    if marker is None:
        # Handle missing marker in some way...
        return {}
    else:
        items = []
        for line in open(marker.args[0]):
            items.append(MyCollectItem.from_dict(json.loads(line)["data"]))
        return items
