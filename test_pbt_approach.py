import pytest
from hypothesis import given
from hypothesis.strategies import integers, text, lists, dictionaries, composite, data, recursive
from utils import *
import json
from string import printable


@given(recursive(dictionaries(text(printable), text(printable), min_size=1),
                 lambda children: lists(children, 1) | dictionaries(text(printable), children, min_size=1)))
@pytest.mark.asyncio
async def test_temp(req):
    wallet_handle, _, _ = await wallet_helper()
    res = await ledger.sign_request(wallet_handle, 'Th7MpTaRZVRYnPiabds81Y', json.dumps(req))
    assert res
