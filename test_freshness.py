import pytest
import time
from indy import did, payment
from utils import *


@pytest.mark.asyncio
async def test_misc_freshness():
    await pool.set_protocol_version(2)
    await payment_initializer('libsovtoken.so', 'sovtoken_init')
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    method = 'sov'
    address1 = await payment.create_payment_address(wallet_handle, method, json.dumps(
        {"seed": str('00000000000000000000000000000000')}))
    address2 = await payment.create_payment_address(wallet_handle, method, json.dumps(
        {"seed": str('11111111111111111111111111111111')}))
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    trustee_did2, trustee_vk2 = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee2')}))
    trustee_did3, trustee_vk3 = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee3')}))
    trustee_did4, trustee_vk4 = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee4')}))

    await nym_helper(pool_handle, wallet_handle, trustee_did, trustee_did2, trustee_vk2, None, 'TRUSTEE')
    await nym_helper(pool_handle, wallet_handle, trustee_did, trustee_did3, trustee_vk3, None, 'TRUSTEE')
    await nym_helper(pool_handle, wallet_handle, trustee_did, trustee_did4, trustee_vk4, None, 'TRUSTEE')

    mint_req, _ = await payment.build_mint_req(wallet_handle, trustee_did,
                                               json.dumps([{"recipient": address1, "amount": 100}]), None)
    mint_req = await ledger.multi_sign_request(wallet_handle, trustee_did, mint_req)
    mint_req = await ledger.multi_sign_request(wallet_handle, trustee_did2, mint_req)
    mint_req = await ledger.multi_sign_request(wallet_handle, trustee_did3, mint_req)
    mint_req = await ledger.multi_sign_request(wallet_handle, trustee_did4, mint_req)

    fees_req = await payment.build_set_txn_fees_req(wallet_handle, trustee_did, method, json.dumps(
        {'1': 0, '100': 0, '101': 0, '102': 0, '113': 0, '114': 0, '10001': 0}))

    fees_req = await ledger.multi_sign_request(wallet_handle, trustee_did, fees_req)
    fees_req = await ledger.multi_sign_request(wallet_handle, trustee_did2, fees_req)
    fees_req = await ledger.multi_sign_request(wallet_handle, trustee_did3, fees_req)
    fees_req = await ledger.multi_sign_request(wallet_handle, trustee_did4, fees_req)

    new_steward_did, new_steward_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    some_did = random_did_and_json()[0]
    await nym_helper(pool_handle, wallet_handle, trustee_did, new_steward_did, new_steward_vk, 'steward', 'STEWARD')

    # # write config ledger txn
    # dests = ['Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv', '8ECVSk179mjsjKRLWiQtssMLgp6EPhWXtaYyStWPSGAb',
    #          'DKVxG2fXXTU8yT5N7hGEbXB3dfdAnYv1JczDUHpmDxya', '4PS3EDQ3dW1tci1Bp6543CfuuebjFrg36kLAUcskGfaA']
    # schedule = json.dumps(dict(
    #     {dest:
    #         datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(days=999, minutes=i*5), '%Y-%m-%dT%H:%M:%S%z')
    #      for dest, i in zip(dests, range(len(dests)))}
    # ))
    # req = await ledger.build_pool_upgrade_request(trustee_did, random_string(10), '9.9.999', 'start',
    #                                               hashlib.sha256().hexdigest(), 5, schedule, None, False, False, None)
    # config_ledger = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    # assert config_ledger['op'] == 'REPLY'

    # write domain ledger txns
    timestamp0 = int(time.time())
    nym = await nym_helper(pool_handle, wallet_handle, trustee_did, some_did)
    attrib = await attrib_helper(pool_handle, wallet_handle, trustee_did, some_did, None, json.dumps({'key': 'value'}),
                                 None)
    schema_id, schema = await schema_helper(pool_handle, wallet_handle, trustee_did, random_string(10), '1.0',
                                            json.dumps(["age", "sex", "height", "name"]))
    temp = await get_schema_helper(pool_handle, wallet_handle, trustee_did, schema_id)
    schema_id, schema_json = await ledger.parse_get_schema_response(json.dumps(temp))
    cred_def_id, _, cred_def =\
        await cred_def_helper(pool_handle, wallet_handle, trustee_did, schema_json, random_string(5), 'CL',
                              json.dumps({'support_revocation': True}))
    revoc_reg_def_id1, _, _, revoc_reg_def =\
        await revoc_reg_def_helper(pool_handle, wallet_handle, trustee_did, 'CL_ACCUM', random_string(5), cred_def_id,
                                   json.dumps({'max_cred_num': 1, 'issuance_type': 'ISSUANCE_BY_DEFAULT'}))
    revoc_reg_def_id2, _, _, revoc_reg_entry =\
        await revoc_reg_entry_helper(pool_handle, wallet_handle, trustee_did, 'CL_ACCUM', random_string(5), cred_def_id,
                                     json.dumps({'max_cred_num': 1, 'issuance_type': 'ISSUANCE_BY_DEFAULT'}))
    timestamp1 = int(time.time())

    add_results = [nym, attrib, schema, cred_def, revoc_reg_def, revoc_reg_entry]
    for res in add_results:
        assert res['op'] == 'REPLY'

    # # write pool ledger txn
    # data = json.dumps(
    #         {
    #               'alias': random_string(5),
    #               'client_ip': '{}.{}.{}.{}'.format(rr(1, 255), 0, 0, rr(1, 255)),
    #               'client_port': rr(1, 32767),
    #               'node_ip': '{}.{}.{}.{}'.format(rr(1, 255), 0, 0, rr(1, 255)),
    #               'node_port': rr(1, 32767),
    #               'services': ['VALIDATOR']
    #         })
    # req = await ledger.build_node_request(new_steward_did, random_did_and_json()[0], data)
    # pool_ledger = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, new_steward_did, req))
    # assert pool_ledger['op'] == 'REPLY'

    # write token ledger txn
    mint = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, mint_req))
    assert mint['op'] == 'REPLY'

    req, _ = await payment.build_get_payment_sources_request(wallet_handle, trustee_did, address1)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req)
    source1 = json.loads(await payment.parse_get_payment_sources_response(method, res))[0]['source']
    req, _ = await payment.build_payment_req(wallet_handle, trustee_did, json.dumps([source1]), json.dumps(
        [{'recipient': address2, 'amount': 100}]), None)
    pay = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    assert pay['op'] == 'REPLY'
    full_receipt = json.loads(await payment.parse_payment_response(method, json.dumps(pay)))

    fees = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, fees_req))
    assert fees['op'] == 'REPLY'

    time.sleep(330)

    # # read config ledger txn - KeyError: 'state_proof'
    # req = await ledger.build_get_txn_request(None, 'CONFIG', config_ledger['result']['txnMetadata']['seqNo'])
    # config_result = json.loads(await ledger.submit_request(pool_handle, req))
    # print(config_result)
    # print(config_result['result']['state_proof']['multi_signature']['value']['timestamp'])
    # print(int(time.time()))
    # assert (int(time.time()) - config_result['result']['state_proof']['multi_signature']['value']['timestamp']) <= 300

    # read domain ledger txns
    get_nym = await get_nym_helper(pool_handle, wallet_handle, trustee_did, some_did)
    get_attrib = await get_attrib_helper(pool_handle, wallet_handle, trustee_did, some_did, None, 'key', None)
    get_schema = await get_schema_helper(pool_handle, wallet_handle, trustee_did, schema_id)
    get_cred_def = await get_cred_def_helper(pool_handle, wallet_handle, trustee_did, cred_def_id)
    get_revoc_reg_def = await get_revoc_reg_def_helper(pool_handle, wallet_handle, trustee_did, revoc_reg_def_id1)
    get_revoc_reg = await get_revoc_reg_helper(pool_handle, wallet_handle, trustee_did, revoc_reg_def_id2, timestamp1)
    get_revoc_reg_delta = await get_revoc_reg_delta_helper(pool_handle, wallet_handle, trustee_did, revoc_reg_def_id2,
                                                           timestamp0, timestamp1)

    get_results = [get_nym, get_attrib, get_schema, get_cred_def, get_revoc_reg_def, get_revoc_reg, get_revoc_reg_delta]
    for res in get_results:
        assert res['result']['seqNo'] is not None
        assert (int(time.time()) - res['result']['state_proof']['multi_signature']['value']['timestamp']) <= 300

    # # read pool ledger txn - KeyError: 'state_proof'
    # req = await ledger.build_get_txn_request(None, 'POOL', pool_ledger['result']['txnMetadata']['seqNo'])
    # pool_result = json.loads(await ledger.submit_request(pool_handle, req))
    # print(pool_result)
    # print(pool_result['result']['state_proof']['multi_signature']['value']['timestamp'])
    # print(int(time.time()))
    # assert (int(time.time()) - pool_result['result']['state_proof']['multi_signature']['value']['timestamp']) <= 300

    # read token ledger txn
    req, _ = await payment.build_get_payment_sources_request(wallet_handle, trustee_did, address1)
    get_mint = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    assert(int(time.time()) - get_mint['result']['state_proof']['multi_signature']['value']['timestamp']) <= 300

    req, _ = await payment.build_verify_payment_req(wallet_handle, trustee_did, full_receipt[0]['receipt'])
    verify = await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req)
    assert verify  # no state_proof

    req = await payment.build_get_txn_fees_req(wallet_handle, trustee_did, method)
    get_fees = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    assert(int(time.time()) - get_fees['result']['state_proof']['multi_signature']['value']['timestamp']) <= 300
