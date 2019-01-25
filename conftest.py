import pytest
import asyncio
from utils import *
from indy import *


@pytest.fixture(scope='module')
def looper():
    looper = asyncio.get_event_loop()
    looper.run_until_complete(pool.set_protocol_version(2))
    yield looper


@pytest.fixture(scope='function')
def pool_handler(looper):
    pool_handle, _ = looper.run_until_complete(pool_helper())
    yield pool_handle


@pytest.fixture(scope='function')
def wallet_handler(looper):
    wallet_handle, _, _ = looper.run_until_complete(wallet_helper())
    yield wallet_handle


@pytest.fixture(scope='function')
def default_trustee(looper, wallet_handler):
    trustee_did, trustee_vk = looper.run_until_complete(
        did.create_and_store_my_did(wallet_handler, json.dumps({'seed': '000000000000000000000000Trustee1'})))
    yield trustee_did, trustee_vk
