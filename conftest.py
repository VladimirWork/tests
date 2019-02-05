import pytest
import testinfra
from utils import *
from indy import *
from async_generator import yield_, async_generator
import time
from random import sample, shuffle
from json import JSONDecodeError


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
