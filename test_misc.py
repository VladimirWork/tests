import pytest
import time
import logging
from indy import did, payment, IndyError
from utils import *
import testinfra
import numpy as np
from random import randrange as rr
from datetime import datetime, timedelta, timezone
import hashlib


# logger = logging.getLogger(__name__)
# logging.basicConfig(level=0, format='%(asctime)s %(message)s')


@pytest.mark.asyncio
async def test_misc_get_nonexistent():
    await pool.set_protocol_version(2)
    timestamp0 = int(time.time())
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    timestamp1 = int(time.time())

    res1 = await get_schema_helper(pool_handle, wallet_handle, submitter_did, 'WKWN6U6XKTFxJBC3mB7Pdo:2:schema1:1.0')
    res2 = await get_cred_def_helper(pool_handle, wallet_handle, submitter_did, '3VTSJXBKw2DBjfaJt4eS1X:3:CL:685:TAG')
    res3 = json.dumps(
        await get_revoc_reg_def_helper(
            pool_handle, wallet_handle, submitter_did,
            'RgTvEeKFSxd2Fcsxh42k9T:4:RgTvEeKFSxd2Fcsxh42k9T:3:CL:689:cred_def_tag:CL_ACCUM:revoc_def_tag'))
    res4 = json.dumps(
        await get_revoc_reg_helper(
            pool_handle, wallet_handle, submitter_did,
            'RgTvEeKFSxd2Fcsxh42k9T:4:RgTvEeKFSxd2Fcsxh42k9T:3:CL:689:cred_def_tag:CL_ACCUM:revoc_def_tag',
            timestamp0))
    res5 = json.dumps(
        await get_revoc_reg_delta_helper(
            pool_handle, wallet_handle, submitter_did,
            'RgTvEeKFSxd2Fcsxh42k9T:4:RgTvEeKFSxd2Fcsxh42k9T:3:CL:689:cred_def_tag:CL_ACCUM:revoc_def_tag',
            timestamp0, timestamp1))

    with pytest.raises(IndyError, match='LedgerNotFound'):
        await ledger.parse_get_schema_response(res1)

    with pytest.raises(IndyError, match='LedgerNotFound'):
        await ledger.parse_get_cred_def_response(res2)

    with pytest.raises(IndyError, match='LedgerNotFound'):
        await ledger.parse_get_revoc_reg_def_response(res3)

    with pytest.raises(IndyError, match='LedgerNotFound'):
        await ledger.parse_get_revoc_reg_response(res4)

    with pytest.raises(IndyError, match='LedgerNotFound'):
        await ledger.parse_get_revoc_reg_delta_response(res5)


@pytest.mark.skip
@pytest.mark.asyncio
async def test_misc_wallet():
    await wallet_helper('cba', 'cba')


@pytest.mark.skip
@pytest.mark.asyncio
async def test_misc_get_txn_by_seqno():
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper(path_to_genesis='/home/indy/stn_genesis')
    req = await ledger.build_get_txn_request(None, None, 9738)
    res = await ledger.submit_request(pool_handle, req)
    print(res)


@pytest.mark.asyncio
async def test_misc_state_proof():
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    random_did = random_did_and_json()[0]
    await nym_helper(pool_handle, wallet_handle, trustee_did, random_did)
    schema_id, _ = await schema_helper(pool_handle, wallet_handle, trustee_did, random_string(10), '1.0',
                                       json.dumps([random_string(1), random_string(2), random_string(3)]))
    time.sleep(1)
    res = json.dumps(await get_schema_helper(pool_handle, wallet_handle, trustee_did, schema_id))
    schema_id, schema_json = await ledger.parse_get_schema_response(res)
    cred_def_id, _, _ = await cred_def_helper(pool_handle, wallet_handle, trustee_did, schema_json, random_string(3),
                                              None, json.dumps({'support_revocation': True}))
    hosts = [testinfra.get_host('docker://node' + str(i)) for i in range(1, 5)]
    print(hosts)
    outputs0 = [host.run('systemctl stop indy-node') for host in hosts[:-1]]
    print(outputs0)

    time.sleep(1)
    try:
        req1 = await ledger.build_get_nym_request(None, random_did)
        res1 = json.loads(await ledger.submit_request(pool_handle, req1))

        req2 = await ledger.build_get_schema_request(None, schema_id)
        res2 = json.loads(await ledger.submit_request(pool_handle, req2))

        req3 = await ledger.build_get_cred_def_request(None, cred_def_id)
        res3 = json.loads(await ledger.submit_request(pool_handle, req3))
    finally:
        outputs1 = [host.run('systemctl start indy-node') for host in hosts[:-1]]
        print(outputs1)

    assert res1['result']['seqNo'] is not None
    assert res2['result']['seqNo'] is not None
    assert res3['result']['seqNo'] is not None

    print(res1)
    print(res2)
    print(res3)


@pytest.mark.asyncio
async def test_misc_stn_slowness():
    await pool.set_protocol_version(2)
    schema_timings = []
    cred_def_timings = []
    nodes = ['NodeTwinPeek', 'RFCU', 'australia', 'brazil', 'canada', 'england', 'ibmTest', 'korea', 'lab10',
             'singapore', 'virginia', 'vnode1', 'xsvalidatorec2irl']
    for i in range(10):
        for node in nodes:
            pool_handle, _ = await pool_helper(path_to_genesis='./stn_genesis', node_list=[node, ])

            t1 = time.perf_counter()
            req1 = await ledger.build_get_schema_request(None,
                                                         'Rvk7x5oSFwoLWZK8rM1Anf:2:Passport Office1539941790480:1.0')
            schema_build_time = time.perf_counter() - t1
            await ledger.submit_request(pool_handle, req1)
            schema_submit_time = time.perf_counter() - t1 - schema_build_time
            schema_timings.append(schema_submit_time)
            print('ITERATION: ', i, '\t', 'NODE: ', node, '\t',
                  'SCHEMA BUILD TIME: ', schema_build_time, '\t', 'SCHEMA SUBMIT TIME: ', schema_submit_time)

            t2 = time.perf_counter()
            req2 = await ledger.build_get_cred_def_request(None, 'Rvk7x5oSFwoLWZK8rM1Anf:3:CL:9726:tag1')
            cred_def_build_time = time.perf_counter() - t2
            await ledger.submit_request(pool_handle, req2)
            cred_def_submit_time = time.perf_counter() - t2 - cred_def_build_time
            cred_def_timings.append(cred_def_submit_time)
            print('ITERATION: ', i, '\t', 'NODE: ', node, '\t',
                  'CRED DEF BUILD TIME: ', cred_def_build_time, '\t', 'CRED DEF SUBMIT TIME: ', cred_def_submit_time)

    print('SCHEMA_SUBMIT_AVG', np.average(schema_timings))
    print('CRED_DEF_SUBMIT_AVG', np.average(cred_def_timings))

    assert np.average(schema_timings) < 1.5
    assert np.average(cred_def_timings) < 0.5


@pytest.mark.asyncio
async def test_new_role():
    # INDY-1916 / IS-1123
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    role_under_test = 'NETWORK_MONITOR'

    did1, vk1 = await did.create_and_store_my_did(wallet_handle, '{}')
    did2, vk2 = await did.create_and_store_my_did(wallet_handle, '{}')
    did3, vk3 = await did.create_and_store_my_did(wallet_handle, '{}')
    did4, vk4 = await did.create_and_store_my_did(wallet_handle, '{}')
    did5, vk5 = await did.create_and_store_my_did(wallet_handle, '{}')

    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    steward_did, steward_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Steward1'}))
    anchor_did, anchor_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    await nym_helper(pool_handle, wallet_handle, trustee_did, anchor_did, anchor_vk, 'trust anchor', 'TRUST_ANCHOR')
    user_did, user_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    await nym_helper(pool_handle, wallet_handle, trustee_did, user_did, user_vk, 'user without role', None)

    # Trustee adds NETWORK_MONITOR NYM
    res1 = await nym_helper(pool_handle, wallet_handle, trustee_did, did1, vk1, None, role_under_test)
    assert res1['op'] == 'REPLY'
    # Steward adds NETWORK_MONITOR NYM
    res2 = await nym_helper(pool_handle, wallet_handle, steward_did, did2, vk2, None, role_under_test)
    assert res2['op'] == 'REPLY'
    # Trust Anchor adds NETWORK_MONITOR NYM - should fail
    res3 = await nym_helper(pool_handle, wallet_handle, anchor_did, did3, vk3, None, role_under_test)
    assert res3['op'] == 'REJECT'
    # User adds NETWORK_MONITOR NYM - should fail
    res4 = await nym_helper(pool_handle, wallet_handle, user_did, did4, vk4, None, role_under_test)
    assert res4['op'] == 'REJECT'
    # NETWORK_MONITOR adds NETWORK_MONITOR NYM - should fail
    res5 = await nym_helper(pool_handle, wallet_handle, did1, did5, vk5, None, role_under_test)
    assert res5['op'] == 'REJECT'

    req = await ledger.build_get_validator_info_request(trustee_did)
    res_t = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    print(res_t)

    req = await ledger.build_get_validator_info_request(steward_did)
    res_s = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, steward_did, req))
    print(res_s)

    req = await ledger.build_get_validator_info_request(did1)
    res_nm = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, did1, req))
    print(res_nm)

    assert res_t.keys() == res_s.keys() == res_nm.keys()

    # NETWORK_MONITOR adds user NYM - should fail
    add_nym = await nym_helper(pool_handle, wallet_handle, did1, did5, vk5, None, None)
    assert add_nym['op'] == 'REJECT'
    # NETWORK_MONITOR sends pool restart - should fail
    req = await ledger.build_pool_restart_request(did1, 'start', '0')
    pool_restart = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, did1, req))
    assert pool_restart['op'] == 'REJECT'
    # NETWORK_MONITOR sends pool config - should fail
    req = await ledger.build_pool_config_request(did1, False, True)
    pool_config = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, did1, req))
    assert pool_config['op'] == 'REQNACK'

    # Trust Anchor removes NETWORK_MONITOR role - should fail
    res6 = await nym_helper(pool_handle, wallet_handle, anchor_did, did1, None, None, '')
    assert res6['op'] == 'REJECT'
    # Trustee removes NETWORK_MONITOR role (that was added by Steward)
    res7 = await nym_helper(pool_handle, wallet_handle, trustee_did, did2, None, None, '')
    assert res7['op'] == 'REPLY'
    # Steward removes NETWORK_MONITOR role (that was added by Trustee)
    res8 = await nym_helper(pool_handle, wallet_handle, steward_did, did1, None, None, '')
    assert res8['op'] == 'REPLY'


@pytest.mark.asyncio
async def test_misc_temp():
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    did1, vk1 = await did.create_and_store_my_did(wallet_handle, '{}')
    did2, vk2 = await did.create_and_store_my_did(wallet_handle, '{}')
    did3, vk3 = await did.create_and_store_my_did(wallet_handle, '{}')
    did4, vk4 = await did.create_and_store_my_did(wallet_handle, '{}')
    did5, vk5 = await did.create_and_store_my_did(wallet_handle, '{}')
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    steward_did, steward_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Steward1'}))
    new_steward_did, new_steward_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    anchor_did, anchor_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    await nym_helper(pool_handle, wallet_handle, trustee_did, new_steward_did, new_steward_vk, 'steward', 'STEWARD')
    await nym_helper(pool_handle, wallet_handle, trustee_did, anchor_did, anchor_vk, 'trust anchor', 'TRUST_ANCHOR')

    req1 = json.dumps({'identifier': trustee_did, 'protocolVersion': 2, 'reqId': int(time.time()),
                       'operation': {'alias': 'network monitor 1',
                                     'type': '1',
                                     'dest': did1,
                                     'role': '201',
                                     'verkey': vk1}})
    res1 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req1))
    assert res1['op'] == 'REPLY'
    req11 = await ledger.build_get_validator_info_request(did1)
    res_nm1 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, did1, req11))
    assert json.loads(res_nm1['Node1'])['op'] == json.loads(res_nm1['Node4'])['op'] == 'REPLY'

    req2 = json.dumps({'identifier': steward_did, 'protocolVersion': 2, 'reqId': int(time.time()),
                       'operation': {'alias': 'network monitor 2',
                                     'type': '1',
                                     'dest': did2,
                                     'role': '201',
                                     'verkey': vk2}})
    res2 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, steward_did, req2))
    assert res2['op'] == 'REPLY'
    req22 = await ledger.build_get_validator_info_request(did2)
    res_nm2 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, did2, req22))
    assert json.loads(res_nm2['Node1'])['op'] == json.loads(res_nm2['Node4'])['op'] == 'REPLY'

    req3 = json.dumps({'identifier': anchor_did, 'protocolVersion': 2, 'reqId': int(time.time()),
                       'operation': {'alias': 'network monitor 3',
                                     'type': '1',
                                     'dest': did3,
                                     'role': '201',
                                     'verkey': vk3}})
    res3 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, anchor_did, req3))
    assert res3['op'] == 'REJECT'
    req33 = await ledger.build_get_validator_info_request(did3)
    res_nm3 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, did3, req33))
    assert json.loads(res_nm3['Node1'])['op'] == json.loads(res_nm3['Node4'])['op'] == 'REQNACK'

    req4 = json.dumps({'identifier': trustee_did, 'protocolVersion': 2, 'reqId': int(time.time()),
                       'operation': {'alias': 'network monitor 1',
                                     'type': '1',
                                     'dest': did4,
                                     'role': '201',
                                     'verkey': vk4}})
    res4 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req4))
    assert res4['op'] == 'REPLY'

    req_t = await ledger.build_get_validator_info_request(trustee_did)
    res_t = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req_t))

    req_s = await ledger.build_get_validator_info_request(steward_did)
    res_s = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, steward_did, req_s))

    assert res_nm1.keys() == res_nm2.keys() == res_t.keys() == res_s.keys()

    # NETWORK_MONITOR adds user NYM - should fail
    add_nym = await nym_helper(pool_handle, wallet_handle, did1, did5, vk5, None, None)
    assert add_nym['op'] == 'REJECT'
    # NETWORK_MONITOR sends pool restart - should fail
    req = await ledger.build_pool_restart_request(did1, 'start', '0')
    pool_restart = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, did1, req))
    assert json.loads(pool_restart['Node1'])['op'] == json.loads(pool_restart['Node4'])['op'] == 'REJECT'
    # NETWORK_MONITOR sends pool config - should fail
    req = await ledger.build_pool_config_request(did1, False, True)
    pool_config1 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, did1, req))
    assert pool_config1['op'] == 'REQNACK'

    # Trustee removes NETWORK_MONITOR role added by him
    res7 = await nym_helper(pool_handle, wallet_handle, trustee_did, did1, None, None, '')
    assert res7['op'] == 'REPLY'
    req7 = await ledger.build_get_validator_info_request(did1)
    res_27 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, did1, req7))
    assert json.loads(res_27['Node1'])['op'] == json.loads(res_27['Node4'])['op'] == 'REJECT'

    # New Steward removes NETWORK_MONITOR role added by another Steward
    res8 = await nym_helper(pool_handle, wallet_handle, new_steward_did, did2, None, None, '')
    assert res8['op'] == 'REPLY'
    req8 = await ledger.build_get_validator_info_request(did2)
    res_18 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, did2, req8))
    assert json.loads(res_18['Node1'])['op'] == json.loads(res_18['Node4'])['op'] == 'REJECT'

    # NM removes NETWORK_MONITOR role from itself
    res9 = await nym_helper(pool_handle, wallet_handle, did4, did4, None, None, '')
    assert res9['op'] == 'REJECT'
    req = await ledger.build_get_validator_info_request(did4)
    res10 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, did4, req))
    assert json.loads(res10['Node1'])['op'] == json.loads(res10['Node4'])['op'] == 'REPLY'


@pytest.mark.asyncio
async def test_misc_pool_config():
    await pool.set_protocol_version(2)
