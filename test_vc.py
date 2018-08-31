import testinfra
import pytest
import time
from utils import *
from indy import did, ledger


@pytest.mark.asyncio
async def test_vc_by_restart():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    random_did = random_did_and_json()[0]
    another_random_did = random_did_and_json()[0]

    add_before = json.loads(await nym_helper(pool_handle, wallet_handle, trustee_did, random_did))
    get_before = json.loads(await get_nym_helper(pool_handle, wallet_handle, trustee_did, random_did))

    req = await ledger.build_get_validator_info_request(trustee_did)
    results = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    result = json.loads(results['Node1'])
    primary = result['result']['data']['Node_info']['Replicas_status']['Node1:0']['Primary'][len('Node'):-len(':0')]
    host = testinfra.get_host('ssh://ubuntu@perf_node'+primary, ssh_config='/home/indy/.ssh/config')
    with host.sudo():
        cmd = host.run('systemctl restart indy-node')
    print(cmd)

    add_after = json.loads(await nym_helper(pool_handle, wallet_handle, trustee_did, another_random_did))
    get_after = json.loads(await get_nym_helper(pool_handle, wallet_handle, trustee_did, another_random_did))

    assert add_before['op'] == 'REPLY'
    assert get_before['result']['seqNo'] is not None
    assert cmd.exit_status == 0
    assert add_after['op'] == 'REPLY'
    assert get_after['result']['seqNo'] is not None


@pytest.mark.asyncio
async def test_vc_by_demotion():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    random_did = random_did_and_json()[0]
    another_random_did = random_did_and_json()[0]

    add_before = json.loads(await nym_helper(pool_handle, wallet_handle, trustee_did, random_did))
    get_before = json.loads(await get_nym_helper(pool_handle, wallet_handle, trustee_did, random_did))

    req = await ledger.build_get_validator_info_request(trustee_did)
    results = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    result = json.loads(results['Node1'])
    primary = result['result']['data']['Node_info']['Replicas_status']['Node1:0']['Primary'][len('Node'):-len(':0')]
    result = json.loads(results['Node'+primary])
    target_did = result['result']['data']['Node_info']['did']
    alias = result['result']['data']['Node_info']['Name']
    data = json.dumps({'alias': alias, 'services': []})
    req = await ledger.build_node_request(trustee_did, target_did, data)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req)

    time.sleep(1)

    add_after = json.loads(await nym_helper(pool_handle, wallet_handle, trustee_did, another_random_did))
    get_after = json.loads(await get_nym_helper(pool_handle, wallet_handle, trustee_did, another_random_did))

    data = json.dumps({'alias': alias, 'services': ['VALIDATOR']})
    req = await ledger.build_node_request(trustee_did, target_did, data)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req)

    assert add_before['op'] == 'REPLY'
    assert get_before['result']['seqNo'] is not None
    assert add_after['op'] == 'REPLY'
    assert get_after['result']['seqNo'] is not None


@pytest.mark.asyncio
async def test_vc_by_degradation():
    pass
