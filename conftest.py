import pytest
from utils import *
from indy import *
from async_generator import yield_, async_generator
import time
from random import sample


@pytest.fixture()
@async_generator
async def pool_handler():
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    await yield_(pool_handle)


@pytest.fixture()
@async_generator
async def wallet_handler():
    wallet_handle, _, _ = await wallet_helper()
    await yield_(wallet_handle)


@pytest.fixture()
@async_generator
async def get_default_trustee(wallet_handler):
    trustee_did, trustee_vk = await default_trustee(wallet_handler)
    await yield_((trustee_did, trustee_vk))


@pytest.fixture()
@async_generator
async def send_and_get_nyms_before_and_after(get_default_trustee, pool_handler, wallet_handler):
    trustee_did, _ = get_default_trustee
    random_did = random_did_and_json()[0]
    another_random_did = random_did_and_json()[0]

    add_before = await nym_helper(pool_handler, wallet_handler, trustee_did, random_did)
    assert add_before['op'] == 'REPLY'
    time.sleep(1)
    get_before = await get_nym_helper(pool_handler, wallet_handler, trustee_did, random_did)
    assert get_before['result']['seqNo'] is not None
    print('\nSEND AND GET NYM SETUP IS DONE!')

    await yield_()

    add_after = await nym_helper(pool_handler, wallet_handler, trustee_did, another_random_did)
    assert add_after['op'] == 'REPLY'
    time.sleep(1)
    get_after = await get_nym_helper(pool_handler, wallet_handler, trustee_did, another_random_did)
    assert get_after['result']['seqNo'] is not None
    print('\nSEND AND GET NYM TEARDOWN IS DONE!')
