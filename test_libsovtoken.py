import time
from utils import *
from indy import pool, did, payment
import pytest


@pytest.mark.asyncio
async def test_libsovtoken_acceptance():
    await pool.set_protocol_version(2)
    await payment_initializer('libsovtoken.so', 'sovtoken_init')
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    payment_method = 'sov'

    trustee_did1, trustee_vk1 = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    trustee_did2, trustee_vk2 = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee2')}))
    trustee_did3, trustee_vk3 = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee3')}))
    trustee_did4, trustee_vk4 = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee4')}))

    await nym_helper(pool_handle, wallet_handle, trustee_did1, trustee_did2, trustee_vk2, None, 'TRUSTEE')
    await nym_helper(pool_handle, wallet_handle, trustee_did1, trustee_did3, trustee_vk3, None, 'TRUSTEE')
    await nym_helper(pool_handle, wallet_handle, trustee_did1, trustee_did4, trustee_vk4, None, 'TRUSTEE')

    req = await payment.build_set_txn_fees_req(wallet_handle, trustee_did1, payment_method, json.dumps(
        {'10001': 5, '102': 3, '101': 2, '1': 1, '100': 4, '113': 6, '114': 7}))

    req = await ledger.multi_sign_request(wallet_handle, trustee_did1, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did2, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did3, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did4, req)

    res2 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req))
    print('\n', 'SET FEES:', res2)

    req = await payment.build_get_txn_fees_req(wallet_handle, trustee_did1, payment_method)
    res3 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req))
    print('\n', 'GET FEES:', res3)

    address1 = await payment.create_payment_address(wallet_handle, payment_method, json.dumps(
        {"seed": str('0000000000000000000000000Wallet3')}))
    address2 = await payment.create_payment_address(wallet_handle, payment_method, json.dumps(
        {"seed": str('0000000000000000000000000Wallet4')}))
    address3 = await payment.create_payment_address(wallet_handle, payment_method, json.dumps(
        {"seed": str('0000000000000000000000000Wallet5')}))
    address4 = await payment.create_payment_address(wallet_handle, payment_method, json.dumps(
        {"seed": str('0000000000000000000000000Wallet6')}))
    print('\n', 'PAYMENT ADDRESSES:', await payment.list_payment_addresses(wallet_handle))

    map1 = {"recipient": address1, "amount": 1}
    map2 = {"recipient": address2, "amount": 2}
    map3 = {"recipient": address3, "amount": 4}
    map4 = {"recipient": address4, "amount": 3}
    list1 = [map1, map2, map3, map4]
    req, _ = await payment.build_mint_req(wallet_handle, trustee_did1,
                                          json.dumps(list1), None)

    req = await ledger.multi_sign_request(wallet_handle, trustee_did1, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did2, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did3, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did4, req)

    res0 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req))
    print('\n', 'MINTING:', res0)

    req, _ = await payment.build_get_payment_sources_request(wallet_handle, trustee_did1, address1)
    res1 = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req)
    source1 = await payment.parse_get_payment_sources_response(payment_method, res1)
    source1 = json.loads(source1)[0]['source']
    print(source1)
    l1 = list()
    l1.append(source1)

    req, _ = await payment.build_get_payment_sources_request(wallet_handle, trustee_did1, address2)
    res2 = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req)
    source2 = await payment.parse_get_payment_sources_response(payment_method, res2)
    source2 = json.loads(source2)[0]['source']
    l2 = list()
    l2.append(source2)

    req, _ = await payment.build_get_payment_sources_request(wallet_handle, trustee_did1, address3)
    res3 = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req)
    source3 = await payment.parse_get_payment_sources_response(payment_method, res3)
    source3 = json.loads(source3)[0]['source']
    l3 = list()
    l3.append(source3)

    req, _ = await payment.build_get_payment_sources_request(wallet_handle, trustee_did1, address4)
    res4 = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req)
    source4 = await payment.parse_get_payment_sources_response(payment_method, res4)
    source4 = json.loads(source4)[0]['source']
    l4 = list()
    l4.append(source4)

    # send schema, no tokens
    _, res = await schema_helper(pool_handle, wallet_handle, trustee_did1, 'gvt', '1.0', json.dumps(["name", "age"]))
    assert json.loads(res)['op'] == 'REJECT'

    # send schema, enough tokens
    schema_id, schema_json = \
        await anoncreds.issuer_create_schema(trustee_did1, 'gvt', '1.0', json.dumps(["name", "age"]))
    req = await ledger.build_schema_request(trustee_did1, schema_json)
    req_with_fees_json, _ = await payment.add_request_fees(wallet_handle, trustee_did1, req, json.dumps(l2), '[]', None)
    res5 = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req_with_fees_json)
    assert res5 is not None

    # get schema
    time.sleep(1)
    res6 = await get_schema_helper(pool_handle, wallet_handle, trustee_did1, schema_id)

    # cred_def incorrect
    schema_id, schema_json = await ledger.parse_get_schema_response(res6)
    cred_def_id, cred_def_json = \
        await anoncreds.issuer_create_and_store_credential_def(wallet_handle, trustee_did1, schema_json, 'TAG',
                                                               'CL', json.dumps({'support_revocation': False}))
    req = await ledger.build_cred_def_request(trustee_did1, cred_def_json)
    req_with_fees_json, _ = await payment.add_request_fees(wallet_handle, trustee_did1, req, json.dumps(l3), '[]', None)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req)
    assert json.loads(res)['op'] == 'REJECT'

    # cred_def correct
    req_with_fees_json, _ = await payment.add_request_fees(wallet_handle, trustee_did1, req, json.dumps(l2), '[]', None)
    res7 = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req)
    assert res7 is not None

    # get cred def
    res8 = await get_cred_def_helper(pool_handle, wallet_handle, trustee_did1, cred_def_id)
    assert res8 is not None

    # send nym with fees
    map5 = {"recipient": address1, "amount": 3}
    l5 = [map5]
    req = await ledger.build_nym_request(trustee_did1, 'V4SGRU86Z58d6TV7PBU111', None, None, None)
    req_with_fees_json, _ = await payment.add_request_fees(wallet_handle, trustee_did1, req, json.dumps(l3),
                                                           json.dumps(l5), None)
    res9 = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req_with_fees_json)
    assert res9 is not None

    # rotate key with fees
    map6 = {"recipient": address1, "amount": 2}
    l6 = [map6]
    res10 = await did.key_for_local_did(wallet_handle, trustee_did2)
    new_key = await did.replace_keys_start(wallet_handle, trustee_did2, json.dumps({}))
    req = await ledger.build_nym_request(trustee_did2, trustee_did2, new_key, None, None)
    req_with_fees_json, _ = await payment.add_request_fees(wallet_handle, trustee_did1, req, json.dumps(l1),
                                                           json.dumps(l6), None)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req_with_fees_json)
    res = await did.replace_keys_apply(wallet_handle, trustee_did2)
    res11 = await did.key_for_local_did(wallet_handle, trustee_did2)
    assert res11 != res10

    # timestamp0 = int(time.time())
    # revoc_reg_def_id, revoc_reg_def_json, revoc_reg_entry_json, res = await revoc_reg_def_helper(pool_handle, wallet_handle, submitter_did, revoc_def_type, tag, cred_def_id, config_json)

    # revoc_reg_def_id, revoc_reg_def_json, revoc_reg_entry_json, res = await revoc_reg_entry_helper(pool_handle, wallet_handle, submitter_did, revoc_def_type, tag, cred_def_id, config_json)

    # assert res0['op'] == 'REPLY'
    # assert res0['result']['txnMetadata']['seqNo'] is not None
