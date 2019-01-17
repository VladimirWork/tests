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
    address = await payment.create_payment_address(wallet_handle, method, json.dumps(
        {"seed": str('00000000000000000000000000000000')}))
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

    req, _ = await payment.build_mint_req(wallet_handle, trustee_did,
                                          json.dumps([{"recipient": address, "amount": 100}]), None)

    req = await ledger.multi_sign_request(wallet_handle, trustee_did, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did2, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did3, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did4, req)
    new_steward_did, new_steward_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    some_did = random_did_and_json()[0]
    res = await nym_helper(pool_handle, wallet_handle, trustee_did, new_steward_did, new_steward_vk,
                           'steward', 'STEWARD')

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

    # write domain ledger txn
    domain_ledger = await nym_helper(pool_handle, wallet_handle, trustee_did, some_did, None, 'some alias', None)
    assert domain_ledger['op'] == 'REPLY'

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
    token_ledger = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    assert token_ledger['op'] == 'REPLY'

    time.sleep(330)

    # # read config ledger txn - KeyError: 'state_proof'
    # req = await ledger.build_get_txn_request(None, 'CONFIG', config_ledger['result']['txnMetadata']['seqNo'])
    # config_result = json.loads(await ledger.submit_request(pool_handle, req))
    # print(config_result)
    # print(config_result['result']['state_proof']['multi_signature']['value']['timestamp'])
    # print(int(time.time()))
    # assert (int(time.time()) - config_result['result']['state_proof']['multi_signature']['value']['timestamp']) <= 300

    # # read domain ledger txn using get_txn - KeyError: 'state_proof'
    # req = await ledger.build_get_txn_request(None, 'DOMAIN', domain_ledger['result']['txnMetadata']['seqNo'])
    # domain_result_get_txn = json.loads(await ledger.submit_request(pool_handle, req))
    # print(domain_result_get_txn['result']['state_proof']['multi_signature']['value']['timestamp'])
    # print(int(time.time()))
    # assert\
    #     (int(time.time()) - domain_result_get_txn['result']['state_proof']['multi_signature']['value']['timestamp'])\
    #     <= 300

    # read domain ledger txn using get_nym
    req = await ledger.build_get_nym_request(None, some_did)
    domain_result_get_nym = json.loads(await ledger.submit_request(pool_handle, req))
    print(domain_result_get_nym['result']['state_proof']['multi_signature']['value']['timestamp'])
    print(int(time.time()))
    assert\
        (int(time.time()) - domain_result_get_nym['result']['state_proof']['multi_signature']['value']['timestamp'])\
        <= 300

    # # read pool ledger txn - KeyError: 'state_proof'
    # req = await ledger.build_get_txn_request(None, 'POOL', pool_ledger['result']['txnMetadata']['seqNo'])
    # pool_result = json.loads(await ledger.submit_request(pool_handle, req))
    # print(pool_result)
    # print(pool_result['result']['state_proof']['multi_signature']['value']['timestamp'])
    # print(int(time.time()))
    # assert (int(time.time()) - pool_result['result']['state_proof']['multi_signature']['value']['timestamp']) <= 300

    # read token ledger txn
    req, _ = await payment.build_get_payment_sources_request(wallet_handle, trustee_did, address)
    token_result = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    print(token_result)
    print(token_result['result']['state_proof']['multi_signature']['value']['timestamp'])
    print(int(time.time()))
    assert\
        (int(time.time()) - token_result['result']['state_proof']['multi_signature']['value']['timestamp'])\
        <= 300
