import pytest
from hypothesis import given
from hypothesis.strategies import text, characters, decimals, composite
from indy import *
import json


@composite
def some_strategy(draw):
    return draw(text().map(lambda x: x+'text'))


@given(name=some_strategy())
@pytest.mark.asyncio
async def test_build_nym_request(name):
    res = await anoncreds.issuer_create_schema('V4SGRU86Z58d6TV7PBUe6f', name, '1.0',
                                               json.dumps(["age", "sex", "height", "name"]))
    assert res
