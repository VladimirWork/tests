from utils import *
import pytest
from indy import pool, wallet, did
import hashlib


async def custom_setup():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    return pool_handle, wallet_handle


async def custom_teardown(wallet_handle, pool_handle):
    await wallet.close_wallet(wallet_handle)
    await pool.close_pool_ledger(pool_handle)


@pytest.mark.asyncio
async def test_send_and_get_nym_positive():
    pool_handle, wallet_handle = await custom_setup()
    test_did, test_vk = await did.create_and_store_my_did(wallet_handle, "{}")
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    res1 = json.loads(await nym_helper(pool_handle, wallet_handle, trustee_did, test_did))
    res2 = json.loads(await get_nym_helper(pool_handle, wallet_handle, test_did, test_did))
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.asyncio
async def test_send_and_get_attrib_positive():
    pool_handle, wallet_handle = await custom_setup()
    test_did, test_vk = await did.create_and_store_my_did(wallet_handle, "{}")
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    hash_ = hashlib.sha256().hexdigest()
    await nym_helper(pool_handle, wallet_handle, trustee_did, test_did, test_vk)
    res1 = json.loads(await attrib_helper(pool_handle, wallet_handle, test_did, test_did, hash_))
    res2 = json.loads(await get_attrib_helper(pool_handle, wallet_handle, test_did, test_did, hash_))
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.asyncio
async def test_send_and_get_schema_positive():
    pass


@pytest.mark.asyncio
async def test_send_and_get_cred_def_positive():
    pass
