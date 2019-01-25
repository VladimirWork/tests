import pytest
from utils import *
from indy import *
from async_generator import yield_, async_generator


@pytest.fixture(scope='function')
@async_generator
async def pool_handler():
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    await yield_(pool_handle)


@pytest.fixture(scope='function')
@async_generator
async def wallet_handler():
    wallet_handle, _, _ = await wallet_helper()
    await yield_(wallet_handle)


@pytest.fixture(scope='function')
@async_generator
async def default_trustee(wallet_handler):
    trustee_did, trustee_vk = await did.create_and_store_my_did(
        wallet_handler, json.dumps({'seed': '000000000000000000000000Trustee1'}))
    await yield_((trustee_did, trustee_vk))
