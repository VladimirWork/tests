from utils import *
import pytest
from indy import pool, did, IndyError
import hashlib
import time
import base58


@pytest.mark.parametrize('submitter_role', ['TRUSTEE', 'STEWARD', 'TRUST_ANCHOR', 'TGB'])
@pytest.mark.asyncio
async def test_send_and_get_nym_positive(submitter_role):
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    await nym_helper(pool_handle, wallet_handle, trustee_did, submitter_did, submitter_vk, None, submitter_role)
    res1 = json.loads(await nym_helper(pool_handle, wallet_handle, submitter_did, target_did))
    res2 = json.loads(await get_nym_helper(pool_handle, wallet_handle, target_did, target_did))
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.parametrize('submitter_seed', ['{}',
                                            json.dumps({'did': base58.b58encode(random_string(16)).decode()}),
                                            json.dumps({'seed': base58.b58encode(random_string(23)).decode()}),
                                            ])
@pytest.mark.asyncio
async def test_send_and_get_nym_negative(submitter_seed):
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, submitter_seed)
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    await nym_helper(pool_handle, wallet_handle, trustee_did, submitter_did, submitter_vk)
    res1 = json.loads(await nym_helper(pool_handle, wallet_handle, submitter_did, target_did))
    res2 = json.loads(await get_nym_helper(pool_handle, wallet_handle, submitter_did, target_did))
    assert res1['op'] == 'REJECT'
    assert res2['result']['seqNo'] is None
    print(res1)
    print(res2)


@pytest.mark.parametrize('xhash, raw, enc', [
    (hashlib.sha256().hexdigest(), None, None),
    (None, json.dumps({'key': 'value'}), None),
    (None, None, 'ENCRYPTED_STRING')
])
@pytest.mark.asyncio
async def test_send_and_get_attrib_positive(xhash, raw, enc):
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    await nym_helper(pool_handle, wallet_handle, submitter_did, target_did, target_vk)
    res1 = json.loads(await attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc))
    res2 = json.loads(await get_attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc))
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.parametrize('xhash, raw, enc, error', [
    (None, None, None, IndyError),
    (hashlib.sha256().hexdigest(), json.dumps({'key': 'value'}), None, None),
    (None, json.dumps({'key': 'value'}), 'ENCRYPTED_STRING', None),
    (hashlib.sha256().hexdigest(), None, 'ENCRYPTED_STRING', None),
    (hashlib.sha256().hexdigest(), json.dumps({'key': 'value'}), 'ENCRYPTED_STRING', None)
])
@pytest.mark.asyncio
async def test_send_and_get_attrib_negative(xhash, raw, enc, error):
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    await nym_helper(pool_handle, wallet_handle, submitter_did, target_did, target_vk)
    if error:
        with pytest.raises(error):
            await attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc)
            await get_attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc)
    else:
        res1 = json.loads(await attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc))
        res2 = json.loads(await get_attrib_helper(pool_handle, wallet_handle, target_did, target_did, xhash, raw, enc))
        assert res1['op'] == 'REQNACK'
        assert res2['op'] == 'REQNACK'
        print(res1)
        print(res2)


@pytest.mark.asyncio
async def test_send_and_get_schema_positive():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    await nym_helper(pool_handle, wallet_handle, submitter_did, target_did, target_vk, None, 'TRUSTEE')
    schema_id, res = await schema_helper(pool_handle, wallet_handle, target_did)
    res1 = json.loads(res)
    res2 = json.loads(await get_schema_helper(pool_handle, wallet_handle, target_did, schema_id))
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.asyncio
async def test_send_and_get_cred_def_positive():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    await nym_helper(pool_handle, wallet_handle, submitter_did, target_did, target_vk, None, 'TRUSTEE')
    schema_id, _ = await schema_helper(pool_handle, wallet_handle, target_did)
    res = await get_schema_helper(pool_handle, wallet_handle, target_did, schema_id)
    schema_id, schema_json = await ledger.parse_get_schema_response(res)
    cred_def_id, _, res = await cred_def_helper(pool_handle, wallet_handle, target_did, schema_json, 'cred_def_tag',
                                                None, json.dumps({'support_revocation': False}))
    res1 = json.loads(res)
    res2 = json.loads(await get_cred_def_helper(pool_handle, wallet_handle, target_did, cred_def_id))
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.asyncio
async def test_send_and_get_revoc_reg_def_positive():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    await nym_helper(pool_handle, wallet_handle, submitter_did, target_did, target_vk, None, 'TRUSTEE')
    schema_id, _ = await schema_helper(pool_handle, wallet_handle, target_did)
    res = await get_schema_helper(pool_handle, wallet_handle, target_did, schema_id)
    schema_id, schema_json = await ledger.parse_get_schema_response(res)
    cred_def_id, _, res = await cred_def_helper(pool_handle, wallet_handle, target_did, schema_json, 'cred_def_tag',
                                                None, json.dumps({"support_revocation": True}))
    revoc_reg_def_id, _, _, res1 = await revoc_reg_def_helper(pool_handle, wallet_handle, target_did, None,
                                                              'revoc_def_tag', cred_def_id,
                                                              json.dumps({'max_cred_num': 1,
                                                                          'issuance_type': 'ISSUANCE_BY_DEFAULT'}))
    res2 = await get_revoc_reg_def_helper(pool_handle, wallet_handle, target_did, revoc_reg_def_id)
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)


@pytest.mark.asyncio
async def test_send_and_get_revoc_reg_entry_positive():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    target_did, target_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    await nym_helper(pool_handle, wallet_handle, submitter_did, target_did, target_vk, None, 'TRUSTEE')
    schema_id, _ = await schema_helper(pool_handle, wallet_handle, target_did)
    res = await get_schema_helper(pool_handle, wallet_handle, target_did, schema_id)
    schema_id, schema_json = await ledger.parse_get_schema_response(res)
    cred_def_id, _, res = await cred_def_helper(pool_handle, wallet_handle, target_did, schema_json, 'cred_def_tag',
                                                'CL', json.dumps({'support_revocation': True}))
    revoc_reg_def_id, _, _, res1 = await revoc_reg_entry_helper(pool_handle, wallet_handle, target_did, 'CL_ACCUM',
                                                                'revoc_def_tag', cred_def_id,
                                                                json.dumps({'max_cred_num': 1,
                                                                            'issuance_type': 'ISSUANCE_BY_DEFAULT'}))
    timestamp = int(time.time())
    res2 = await get_revoc_reg_helper(pool_handle, wallet_handle, target_did, revoc_reg_def_id, timestamp)
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)
