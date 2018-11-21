import pytest
import time
import logging
from indy import did, IndyError
from utils import *
import testinfra

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


@pytest.mark.asyncio
async def test_misc_wallet():
    await wallet_helper('cba', 'cba')


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

    hosts = [testinfra.get_host('docker://node' + str(i)) for i in range(1, 5)]
    print(hosts)
    outputs0 = [host.run('systemctl stop indy-node') for host in hosts[:-1]]
    print(outputs0)

    time.sleep(1)
    try:
        req = await ledger.build_get_nym_request(None, random_did)
        res = json.loads(await ledger.submit_request(pool_handle, req))
    finally:
        outputs1 = [host.run('systemctl start indy-node') for host in hosts[:-1]]
        print(outputs1)

    assert res['result']['seqNo'] is not None

    print(res)


@pytest.mark.asyncio
async def test_misc_stn_slowness():
    await pool.set_protocol_version(2)
    nodes = ['NodeTwinPeek', 'RFCU', 'australia', 'brazil', 'canada', 'england', 'ibmTest', 'korea', 'lab10',
             'singapore', 'virginia', 'vnode1', 'xsvalidatorec2irl']
    for i in range(5):
        for node in nodes:
            # pool_handle, _ = await pool_helper(path_to_genesis='/home/indy/stn_genesis', node_list=nodes)
            pool_handle, _ = await pool_helper(path_to_genesis='/home/indy/stn_genesis', node_list=[].append(node))

            t1 = time.perf_counter()
            req1 = await ledger.build_get_schema_request(None,
                                                         'Rvk7x5oSFwoLWZK8rM1Anf:2:Passport Office1539941790480:1.0')
            schema_build_time = time.perf_counter() - t1
            await ledger.submit_request(pool_handle, req1)
            schema_submit_time = time.perf_counter() - t1 - schema_build_time
            print('ITERATION: ', i, '\t', 'NODE: ', node, '\t',
                  'SCHEMA BUILD TIME: ', schema_build_time, '\t', 'SCHEMA SUBMIT TIME: ', schema_submit_time)

            t2 = time.perf_counter()
            req2 = await ledger.build_get_cred_def_request(None, 'Rvk7x5oSFwoLWZK8rM1Anf:3:CL:9726:tag1')
            cred_def_build_time = time.perf_counter() - t2
            await ledger.submit_request(pool_handle, req2)
            cred_def_submit_time = time.perf_counter() - t2 - cred_def_build_time
            print('ITERATION: ', i, '\t', 'NODE: ', node, '\t',
                  'CRED DEF BUILD TIME: ', cred_def_build_time, '\t', 'CRED DEF SUBMIT TIME: ', cred_def_submit_time)
