from utils import *
from indy import pool, did, payment
import pytest
from ctypes import CDLL


@pytest.mark.asyncio
async def test_payments_basic():
    await pool.set_protocol_version(2)
    library_name, initializer_name = 'libsovtoken.so', 'sovtoken_init'
    library = CDLL(library_name)
    init = getattr(library, initializer_name)
    init()
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    method = 'sov'
    address = await payment.create_payment_address(wallet_handle, method, json.dumps(
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

    req, _ = await payment.build_mint_req(wallet_handle, trustee_did1,
                                          json.dumps([{"recipient": address, "amount": 100}]), None)

    req = await ledger.multi_sign_request(wallet_handle, trustee_did1, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did2, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did3, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did4, req)

    res0 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req))
    print('\n', 'MINTING:', res0)

    req, _ = await payment.build_get_payment_sources_request(wallet_handle, trustee_did1, address)
    res1 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req))
    print('\n', 'SOURCES:', res1)

    req = await payment.build_set_txn_fees_req(wallet_handle, trustee_did1, method, json.dumps({'113': 1, '114': 1}))

    req = await ledger.multi_sign_request(wallet_handle, trustee_did1, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did2, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did3, req)
    req = await ledger.multi_sign_request(wallet_handle, trustee_did4, req)

    res2 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req))
    print('\n', 'SET FEES:', res2)

    req = await payment.build_get_txn_fees_req(wallet_handle, trustee_did1, method)
    res3 = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did1, req))
    print('\n', 'GET FEES:', res3)

    assert res0['op'] == 'REPLY'
    assert res0['result']['txnMetadata']['seqNo'] is not None
    assert res1['op'] == 'REPLY'
    assert res2['op'] == 'REPLY'
    assert res2['result']['txnMetadata']['seqNo'] is not None
    assert res3['op'] == 'REPLY'


async def test_build_mint_req_positive():
    pass


async def test_build_mint_req_negative():
    pass


async def test_create_and_list_payment_address_positive():
    pass


async def test_create_and_list_payment_address_negative():
    pass


async def test_add_request_fees_and_parse_response_with_fees_positive():
    pass


async def test_add_request_fees_and_parse_response_with_fees_negative():
    pass


async def test_build_and_parse_get_payment_sources_positive():
    pass


async def test_build_and_parse_get_payment_sources_negative():
    pass


async def test_build_payment_req_and_parse_payment_response_positive():
    pass


async def test_build_payment_req_and_parse_payment_response_negative():
    pass


async def test_set_get_parse_txn_fees_positive():
    pass


async def test_set_get_parse_txn_fees_negative():
    pass


async def test_build_and_parse_verify_payment_positive():
    pass


async def test_build_and_parse_verify_payment_negative():
    pass
