import testinfra
import pytest
import time
from utils import *
from indy import ledger
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=0, format='%(asctime)s %(message)s')


@pytest.mark.asyncio
async def test_vc_by_restart(pool_handler, wallet_handler, get_default_trustee, send_and_get_nyms_before_and_after,
                             stop_and_start_primary):
    time.sleep(120)


@pytest.mark.asyncio
async def test_vc_by_demotion(pool_handler, wallet_handler):
    trustee_did, trustee_vk = await default_trustee(wallet_handler)
    random_did = random_did_and_json()[0]
    another_random_did = random_did_and_json()[0]

    add_before = await nym_helper(pool_handler, wallet_handler, trustee_did, random_did)
    time.sleep(3)
    get_before = await get_nym_helper(pool_handler, wallet_handler, trustee_did, random_did)

    print(add_before, '\n', get_before)

    req_vi = await ledger.build_get_validator_info_request(trustee_did)
    results = json.loads(await ledger.sign_and_submit_request(pool_handler, wallet_handler, trustee_did, req_vi))
    result = json.loads(results['Node4'])
    primary_before =\
        result['result']['data']['Node_info']['Replicas_status']['Node4:0']['Primary'][len('Node'):-len(':0')]
    res = json.loads(results['Node'+primary_before])
    target_did = res['result']['data']['Node_info']['did']
    alias = res['result']['data']['Node_info']['Name']
    demote_data = json.dumps({'alias': alias, 'services': []})
    demote_req = await ledger.build_node_request(trustee_did, target_did, demote_data)
    demote_res = json.loads(await ledger.sign_and_submit_request(pool_handler, wallet_handler, trustee_did, demote_req))
    assert demote_res['op'] == 'REPLY'

    time.sleep(120)

    add_after = await nym_helper(pool_handler, wallet_handler, trustee_did, another_random_did)
    time.sleep(3)
    get_after = await get_nym_helper(pool_handler, wallet_handler, trustee_did, another_random_did)

    print(add_after, '\n', get_after)

    promote_data = json.dumps({'alias': alias, 'services': ['VALIDATOR']})
    promote_req = await ledger.build_node_request(trustee_did, target_did, promote_data)
    promote_res = json.loads(await ledger.sign_and_submit_request(pool_handler, wallet_handler, trustee_did, promote_req))
    assert promote_res['op'] == 'REPLY'

    results = json.loads(await ledger.sign_and_submit_request(pool_handler, wallet_handler, trustee_did, req_vi))
    result = json.loads(results['Node4'])
    primary_after =\
        result['result']['data']['Node_info']['Replicas_status']['Node4:0']['Primary'][len('Node'):-len(':0')]

    assert add_before['op'] == 'REPLY'
    assert get_before['result']['seqNo'] is not None
    assert add_after['op'] == 'REPLY'
    assert get_after['result']['seqNo'] is not None
    assert primary_before != primary_after

    print(primary_before)
    print(primary_after)
