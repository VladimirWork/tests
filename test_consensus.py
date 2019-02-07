import pytest
from utils import *
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=0, format='%(asctime)s %(message)s')


@pytest.mark.asyncio
async def test_consensus_restore_after_f_plus_one(pool_handler, wallet_handler, get_default_trustee):
    trustee_did, _ = get_default_trustee
    did1 = random_did_and_json()[0]
    did2 = random_did_and_json()[0]
    did3 = random_did_and_json()[0]
    hosts = [testinfra.get_host('docker://node' + str(i)) for i in range(1, 5)]

    try:
        # 4/4 online - can w+r
        await send_and_get_nym(pool_handler, wallet_handler, trustee_did, did1)
        # 3/4 online - can w+r
        hosts[3].run('systemctl stop indy-node')
        await send_and_get_nym(pool_handler, wallet_handler, trustee_did, did2)
        # 2/4 online - can r
        hosts[2].run('systemctl stop indy-node')
        res = await get_nym_helper(pool_handler, wallet_handler, trustee_did, did1)
        assert res['result']['seqNo'] is not None
        # 4/4 online - can w+r
        hosts[3].run('systemctl start indy-node')
        hosts[2].run('systemctl start indy-node')
        await send_and_get_nym(pool_handler, wallet_handler, trustee_did, did3)
    finally:
        outputs = [host.run('systemctl start indy-node') for host in hosts]
        assert outputs


@pytest.mark.asyncio
async def test_consensus_state_proof_reading(pool_handler, wallet_handler, get_default_trustee):
    trustee_did, _ = get_default_trustee
    did1 = random_did_and_json()[0]
    did2 = random_did_and_json()[0]
    hosts = [testinfra.get_host('docker://node' + str(i)) for i in range(1, 5)]

    try:
        await send_and_get_nym(pool_handler, wallet_handler, trustee_did, did1)
        time.sleep(5)
        # Stop all except 1
        outputs = [host.run('systemctl stop indy-node') for host in hosts[1:]]
        assert outputs
        time.sleep(5)
        res = await get_nym_helper(pool_handler, wallet_handler, trustee_did, did1)
        assert res['result']['seqNo'] is not None
        # Stop the last one
        hosts[0].run('systemctl stop indy-node')
        # Start all
        outputs = [host.run('systemctl start indy-node') for host in hosts]
        assert outputs
        time.sleep(5)
        await send_and_get_nym(pool_handler, wallet_handler, trustee_did, did2)
    finally:
        outputs = [host.run('systemctl start indy-node') for host in hosts]
        assert outputs


@pytest.mark.asyncio
async def test_consensus_n_and_f_changing(pool_handler, wallet_handler, get_default_trustee):
    trustee_did, _ = get_default_trustee
    did1 = random_did_and_json()[0]
    did2 = random_did_and_json()[0]
    hosts = [testinfra.get_host('docker://node' + str(i)) for i in range(1, 8)]
