import pytest
from utils import *


@pytest.mark.asyncio
async def test_misc_roles(pool_handler, wallet_handler, get_default_trustee):
    trustee_did, _ = get_default_trustee
    new_steward_did, new_steward_vk = await did.create_and_store_my_did(wallet_handler, '{}')
    anchor1_did, anchor1_vk = await did.create_and_store_my_did(wallet_handler, '{}')
    anchor2_did, anchor2_vk = await did.create_and_store_my_did(wallet_handler, '{}')

    # Trustee adds new Steward
    res1 = await nym_helper(pool_handler, wallet_handler, trustee_did, new_steward_did, new_steward_vk, None,
                            'STEWARD')
    assert res1['op'] == 'REPLY'

    # New Steward adds TA1
    res2 = await nym_helper(pool_handler, wallet_handler, new_steward_did, anchor1_did, anchor1_vk, None,
                            'TRUST_ANCHOR')
    assert res2['op'] == 'REPLY'

    # Trustee removes new Steward
    res3 = await nym_helper(pool_handler, wallet_handler, trustee_did, new_steward_did, None, None,
                            '')
    assert res3['op'] == 'REPLY'

    # New Steward try to add TA2
    res4 = await nym_helper(pool_handler, wallet_handler, new_steward_did, anchor2_did, anchor2_vk, None,
                            'TRUST_ANCHOR')
    assert res4['op'] == 'REJECT'
