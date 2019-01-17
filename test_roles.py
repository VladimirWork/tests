import pytest
from indy import did
from utils import *


@pytest.mark.asyncio
async def test_misc_roles():
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    new_steward_did, new_steward_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    anchor1_did, anchor1_vk = await did.create_and_store_my_did(wallet_handle, '{}')
    anchor2_did, anchor2_vk = await did.create_and_store_my_did(wallet_handle, '{}')

    # Trustee adds new Steward
    res1 = await nym_helper(pool_handle, wallet_handle, trustee_did, new_steward_did, new_steward_vk, None, 'STEWARD')
    assert res1['op'] == 'REPLY'

    # New Steward adds TA1
    res2 = await nym_helper(pool_handle, wallet_handle, new_steward_did, anchor1_did, anchor1_vk, None, 'TRUST_ANCHOR')
    assert res2['op'] == 'REPLY'

    # Trustee removes new Steward
    res3 = await nym_helper(pool_handle, wallet_handle, trustee_did, new_steward_did, None, None, '')
    assert res3['op'] == 'REPLY'

    # New Steward adds TA2
    res4 = await nym_helper(pool_handle, wallet_handle, new_steward_did, anchor2_did, anchor2_vk, None, 'TRUST_ANCHOR')
    assert res4['op'] == 'REJECT'
