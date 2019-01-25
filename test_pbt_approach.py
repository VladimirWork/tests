import pytest
from hypothesis import given
from hypothesis.strategies import text
from indy import *


@given(text(), text(), text(), text(), text())
@pytest.mark.trio
async def test_build_nym_request(submitter_did, target_did, ver_key, alias, role):
    res = await ledger.build_nym_request(submitter_did, target_did, ver_key, alias, role)
    assert res
