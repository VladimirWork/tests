import pytest
from indy import did, IndyError
from utils import *


@pytest.mark.asyncio
async def test_misc_get_nonexistent():
    await pool.set_protocol_version(2)
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))

    res1 = await get_schema_helper(pool_handle, wallet_handle, submitter_did, '7kqbG8zcdAMc9Q6SMU4xZy:2:schema1:1.0')
    res2 = await get_cred_def_helper(pool_handle, wallet_handle, submitter_did, 'VRaXpAenQy5gK8mNDUdJe8:3:CL:20')

    with pytest.raises(IndyError, match='LedgerNotFound') as IE1:
        await ledger.parse_get_schema_response(res1)

    with pytest.raises(IndyError, match='LedgerNotFound') as IE2:
        await ledger.parse_get_cred_def_response(res2)

    print(res1, '\n', IE1)
    print(res2, '\n', IE2)


@pytest.mark.asyncio
async def test_misc_wallet():
    await wallet_helper('abc', 'abc',)
