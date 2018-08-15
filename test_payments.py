from utils import *
from indy import pool, did, payment
import pytest
from ctypes import CDLL


@pytest.mark.asyncio
async def test_payments_state_proofs():
    await pool.set_protocol_version(2)
    library_name, initializer_name = 'libsovtoken.so', 'sovtoken_init'
    library = CDLL(library_name)
    init = getattr(library, initializer_name)
    init()
    pool_handle = await pool_helper()
    wallet_handle = await wallet_helper()
    address = await payment.create_payment_address(wallet_handle, 'sov', json.dumps(
        {"seed": str('00000000000000000000000000000000')}))

    trustee_did1, trustee_vk1 = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    trustee_did2, trustee_vk2 = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee2')}))
    trustee_did3, trustee_vk3 = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee3')}))
    trustee_did4, trustee_vk4 = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee4')}))

    await nym_helper(pool_handle, wallet_handle, trustee_did1, trustee_did2, trustee_vk2, None, 'TRUSTEE')
    await nym_helper(pool_handle, wallet_handle, trustee_did1, trustee_did3, trustee_vk3, None, 'TRUSTEE')
    await nym_helper(pool_handle, wallet_handle, trustee_did1, trustee_did4, trustee_vk4, None, 'TRUSTEE')

    req1, _ = await payment.build_mint_req(wallet_handle, trustee_did1,
                                           json.dumps([{"recipient": address, "amount": 100}]), None)

    req2 = await ledger.multi_sign_request(wallet_handle, trustee_did1, req1)
    req3 = await ledger.multi_sign_request(wallet_handle, trustee_did2, req2)
    req4 = await ledger.multi_sign_request(wallet_handle, trustee_did3, req3)
    req5 = await ledger.multi_sign_request(wallet_handle, trustee_did4, req4)

    await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req5)

    req, _ = await payment.build_get_payment_sources_request(wallet_handle, trustee_did1, address)
    res1 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req))
    print('\n', res1)
    assert res1['op'] == 'REPLY'

    req = await  payment.build_get_txn_fees_req(wallet_handle, trustee_did1, 'sov')
    res2 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req))
    print('\n', res2)
    assert res2['op'] == 'REPLY'
