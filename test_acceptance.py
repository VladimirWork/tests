from utils import *
from indy import pool, did
import time
import pytest


@pytest.mark.asyncio
async def test_connections_count():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    time.sleep(5)
    res1 = json.loads(await get_nym_helper(pool_handle, wallet_handle, trustee_did, 'Th7MpTaRZVRYnPiabds81Y'))
    res2 = json.loads(await get_nym_helper(pool_handle, wallet_handle, trustee_did, 'EbP4aYNeTHL6q385GuVpRV'))
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    print(res1)
    print(res2)
