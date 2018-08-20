from utils import *
import pytest
from indy import pool, did, IndyError
import hashlib
import time


@pytest.mark.asyncio
async def test_send_and_get_nym_positive():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    test_did, test_vk = await did.create_and_store_my_did(wallet_handle, "{}")
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    res1 = json.loads(await nym_helper(pool_handle, wallet_handle, trustee_did, test_did))
    res2 = json.loads(await get_nym_helper(pool_handle, wallet_handle, test_did, test_did))
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.parametrize('submitter_seed', ["{}",
                                            json.dumps({"did": str('1111111111111111')}),
                                            json.dumps({"seed": str('00000000000000000000000000000000')}),
                                            ])
@pytest.mark.parametrize('target_seed', ["{}"])
@pytest.mark.asyncio
async def test_send_and_get_nym_negative(submitter_seed, target_seed):
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    test_did, test_vk = await did.create_and_store_my_did(wallet_handle, target_seed)
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, submitter_seed)
    res1 = json.loads(await nym_helper(pool_handle, wallet_handle, trustee_did, test_did))
    res2 = json.loads(await get_nym_helper(pool_handle, wallet_handle, test_did, test_did))
    assert res1['op'] == 'REQNACK'
    assert res2['result']['seqNo'] is None
    print(res1)
    print(res2)


@pytest.mark.asyncio
async def test_send_and_get_attrib_positive():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
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
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    test_did, test_vk = await did.create_and_store_my_did(wallet_handle, "{}")
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    await nym_helper(pool_handle, wallet_handle, trustee_did, test_did, test_vk, None, 'TRUSTEE')
    schema_id, res = await schema_helper(pool_handle, wallet_handle, test_did)
    res1 = json.loads(res)
    res2 = json.loads(await get_schema_helper(pool_handle, wallet_handle, test_did, schema_id))
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.asyncio
async def test_send_and_get_cred_def_positive():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    test_did, test_vk = await did.create_and_store_my_did(wallet_handle, "{}")
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    await nym_helper(pool_handle, wallet_handle, trustee_did, test_did, test_vk, None, 'TRUSTEE')
    schema_id, _ = await schema_helper(pool_handle, wallet_handle, test_did)
    res = await get_schema_helper(pool_handle, wallet_handle, test_did, schema_id)
    schema_id, schema_json = await ledger.parse_get_schema_response(res)
    cred_def_id, _, res = await cred_def_helper(pool_handle, wallet_handle, test_did, schema_json, 'cred_def_tag', None,
                                             json.dumps({"support_revocation": False}))
    res1 = json.loads(res)
    res2 = json.loads(await get_cred_def_helper(pool_handle, wallet_handle, test_did, cred_def_id))
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.asyncio
async def test_send_and_get_revoc_reg_def_positive():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    test_did, test_vk = await did.create_and_store_my_did(wallet_handle, "{}")
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    await nym_helper(pool_handle, wallet_handle, trustee_did, test_did, test_vk, None, 'TRUSTEE')
    schema_id, _ = await schema_helper(pool_handle, wallet_handle, test_did)
    res = await get_schema_helper(pool_handle, wallet_handle, test_did, schema_id)
    schema_id, schema_json = await ledger.parse_get_schema_response(res)
    cred_def_id, _, res = await cred_def_helper(pool_handle, wallet_handle, test_did, schema_json, 'cred_def_tag', None,
                                                json.dumps({"support_revocation": True}))
    revoc_reg_def_id, _, _, res1 = await revoc_reg_def_helper(pool_handle, wallet_handle, test_did, None,
                                                              'revoc_def_tag', cred_def_id,
                                                              json.dumps({"max_cred_num": 1,
                                                                          "issuance_type": "ISSUANCE_BY_DEFAULT"}))
    res2 = await get_revoc_reg_def_helper(pool_handle, wallet_handle, test_did, revoc_reg_def_id)
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.asyncio
async def test_send_and_get_revoc_reg_entry_positive():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    test_did, test_vk = await did.create_and_store_my_did(wallet_handle, "{}")
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    await nym_helper(pool_handle, wallet_handle, trustee_did, test_did, test_vk, None, 'TRUSTEE')
    schema_id, _ = await schema_helper(pool_handle, wallet_handle, test_did)
    res = await get_schema_helper(pool_handle, wallet_handle, test_did, schema_id)
    schema_id, schema_json = await ledger.parse_get_schema_response(res)
    cred_def_id, _, res = await cred_def_helper(pool_handle, wallet_handle, test_did, schema_json, 'cred_def_tag',
                                                'CL', json.dumps({"support_revocation": True}))
    revoc_reg_def_id, _, _, res1 = await revoc_reg_entry_helper(pool_handle, wallet_handle, test_did, 'CL_ACCUM',
                                                                'revoc_def_tag', cred_def_id,
                                                                json.dumps({"max_cred_num": 1,
                                                                            "issuance_type": "ISSUANCE_BY_DEFAULT"}))
    timestamp = int(time.time())
    res2 = await get_revoc_reg_helper(pool_handle, wallet_handle, test_did, revoc_reg_def_id, timestamp)
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)
