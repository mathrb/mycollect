import pytest
from mycollect.starter import main_loop

@pytest.mark.asyncio
async def test_main_loop():
    await main_loop("tests/test_files/sample_config.yaml", False)