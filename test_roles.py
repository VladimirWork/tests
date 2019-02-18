import pytest
from utils import *


@pytest.mark.asyncio
async def test_roles(pool_handler, wallet_handler, get_default_trustee):
    trustee_did, _ = get_default_trustee
    trustee1_did, trustee1_vk = await did.create_and_store_my_did(wallet_handler, '{}')
    steward1_did, steward1_vk = await did.create_and_store_my_did(wallet_handler, '{}')
    anchor1_did, anchor1_vk = await did.create_and_store_my_did(wallet_handler, '{}')
    identity1_did, identity1_vk = await did.create_and_store_my_did(wallet_handler, '{}')
    steward2_did, steward2_vk = await did.create_and_store_my_did(wallet_handler, '{}')
    anchor2_did, anchor2_vk = await did.create_and_store_my_did(wallet_handler, '{}')
    anchor3_did, anchor3_vk = await did.create_and_store_my_did(wallet_handler, '{}')
    identity2_did, identity2_vk = await did.create_and_store_my_did(wallet_handler, '{}')
    identity3_did, identity3_vk = await did.create_and_store_my_did(wallet_handler, '{}')
    identity4_did, identity4_vk = await did.create_and_store_my_did(wallet_handler, '{}')

    # <<< TRUSTEE cases >>>
    # Default Trustee adds Trustee1
    res1 = await nym_helper(pool_handler, wallet_handler, trustee_did, trustee1_did, trustee1_vk, None, 'TRUSTEE')
    assert res1['op'] == 'REPLY'
    # Trustee1 adds Steward1
    res2 = await nym_helper(pool_handler, wallet_handler, trustee1_did, steward1_did, steward1_vk, None, 'STEWARD')
    assert res2['op'] == 'REPLY'
    # Trustee1 adds TrustAnchor1
    res3 = await nym_helper(pool_handler, wallet_handler, trustee1_did, anchor1_did, anchor1_vk, None, 'TRUST_ANCHOR')
    assert res3['op'] == 'REPLY'
    # Trustee1 adds IdentityOwner1
    res4 = await nym_helper(pool_handler, wallet_handler, trustee1_did, identity1_did, identity1_vk, None, None)
    assert res4['op'] == 'REPLY'
    # Steward1 tries to demote Trustee1 - should fail
    res5 = await nym_helper(pool_handler, wallet_handler, steward1_did, trustee1_did, None, None, '')
    assert res5['op'] == 'REJECT'
    # Default Trustee demotes Trustee1
    res6 = await nym_helper(pool_handler, wallet_handler, trustee_did, trustee1_did, None, None, '')
    assert res6['op'] == 'REPLY'
    # Trustee1 tries to add Steward2 after demotion - should fail
    res7 = await nym_helper(pool_handler, wallet_handler, trustee1_did, steward2_did, steward2_did, None, 'STEWARD')
    assert res7['op'] == 'REJECT'
    # Trustee1 tries to demote Steward1 after demotion - should fail
    res8 = await nym_helper(pool_handler, wallet_handler, trustee1_did, steward1_did, None, None, '')
    assert res8['op'] == 'REJECT'
    # Default Trustee promotes Trustee1 back
    res9 = await nym_helper(pool_handler, wallet_handler, trustee_did, trustee1_did, None, None, 'TRUSTEE')
    assert res9['op'] == 'REPLY'
    # Trustee1 adds Steward2 after promotion
    res10 = await nym_helper(pool_handler, wallet_handler, trustee1_did, steward2_did, steward2_did, None, 'STEWARD')
    assert res10['op'] == 'REPLY'

    # <<< STEWARD cases >>>
    # Steward1 adds TrustAnchor2
    res11 = await nym_helper(pool_handler, wallet_handler, steward1_did, anchor2_did, anchor2_vk, None, 'TRUST_ANCHOR')
    assert res11['op'] == 'REPLY'
    # Steward1 adds IdentityOwner2
    res12 = await nym_helper(pool_handler, wallet_handler, steward1_did, identity2_did, identity2_vk, None, None)
    assert res12['op'] == 'REPLY'
    # TrustAnchor1 tries to demote Steward1 - should fail
    res13 = await nym_helper(pool_handler, wallet_handler, anchor1_did, steward1_did, None, None, '')
    assert res13['op'] == 'REJECT'
    # Trustee1 demotes Steward1
    res14 = await nym_helper(pool_handler, wallet_handler, trustee1_did, steward1_did, None, None, '')
    assert res14['op'] == 'REPLY'
    # Steward1 tries to add TrustAnchor3 after demotion - should fail
    res15 = await nym_helper(pool_handler, wallet_handler, steward1_did, anchor3_did, anchor3_vk, None, 'TRUST_ANCHOR')
    assert res15['op'] == 'REJECT'
    # Steward1 tries to demote TrustAnchor2 after demotion - should fail
    res16 = await nym_helper(pool_handler, wallet_handler, steward1_did, anchor2_did, None, None, '')
    assert res16['op'] == 'REJECT'
    # Trustee1 promotes Steward1 back
    res17 = await nym_helper(pool_handler, wallet_handler, trustee1_did, steward1_did, None, None, 'STEWARD')
    assert res17['op'] == 'REPLY'
    # Steward1 adds TrustAnchor3 after promotion
    res18 = await nym_helper(pool_handler, wallet_handler, steward1_did, anchor3_did, anchor3_vk, None, 'TRUST_ANCHOR')
    assert res18['op'] == 'REPLY'

    # <<< TRUST_ANCHOR cases >>>
    # TrustAnchor1 adds IdentityOwner3
    res19 = await nym_helper(pool_handler, wallet_handler, anchor1_did, identity3_did, identity3_vk, None, None)
    assert res19['op'] == 'REPLY'
    # IdentityOwner1 tries to demote TrustAnchor1 - should fail
    res20 = await nym_helper(pool_handler, wallet_handler, identity1_did, anchor1_did, None, None, '')
    assert res20['op'] == 'REJECT'
    # Trustee1 demotes TrustAnchor1
    res21 = await nym_helper(pool_handler, wallet_handler, trustee1_did, anchor1_did, None, None, '')
    assert res21['op'] == 'REPLY'
    # TrustAnchor1 tries to add IdentityOwner4 after demotion - should fail
    res22 = await nym_helper(pool_handler, wallet_handler, anchor1_did, identity4_did, identity4_vk, None, None)
    assert res22['op'] == 'REJECT'
    # Trustee1 promotes TrustAnchor1 back
    res23 = await nym_helper(pool_handler, wallet_handler, trustee1_did, anchor1_did, None, None, 'TRUST_ANCHOR')
    assert res23['op'] == 'REPLY'
    # TrustAnchor1 adds IdentityOwner4 after promotion
    res24 = await nym_helper(pool_handler, wallet_handler, anchor1_did, identity4_did, identity4_vk, None, None)
    assert res24['op'] == 'REPLY'
