import pytest
from hypothesis import given
from hypothesis.strategies import text, characters, decimals
from indy import *
import json


@given(text().map(lambda x: x + 'text'))
@pytest.mark.asyncio
async def test_build_nym_request(name):
    res = await anoncreds.issuer_create_schema('V4SGRU86Z58d6TV7PBUe6f', name, '1.0',
                                               json.dumps(["age", "sex", "height", "name"]))
    assert res
