import pytest
from hypothesis import given
from hypothesis.strategies import text
from indy import *
import functools
import asyncio


def run_in_event_loop(async_func):
    @functools.wraps(async_func)
    def wrapped(operations, queue_size, add_size, get_size, event_loop):
        event_loop.run_until_complete(asyncio.ensure_future(
            async_func(operations, queue_size, add_size, get_size, event_loop),
            loop=event_loop,
        ))
    return wrapped


@given(text(), text(), text(), text(), text())
@run_in_event_loop
@pytest.mark.asyncio
async def test_build_nym_request(submitter_did, target_did, ver_key, alias, role):
    res = await ledger.build_nym_request(submitter_did, target_did, ver_key, alias, role)
    assert res
