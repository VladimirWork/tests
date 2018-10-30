import pytest
import time
from indy import did, IndyError
from utils import *


@pytest.mark.asyncio
async def test_misc_get_nonexistent():
    await pool.set_protocol_version(2)
    timestamp0 = int(time.time())
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    timestamp1 = int(time.time())

    res1 = await get_schema_helper(pool_handle, wallet_handle, submitter_did, 'WKWN6U6XKTFxJBC3mB7Pdo:2:schema1:1.0')
    res2 = await get_cred_def_helper(pool_handle, wallet_handle, submitter_did, '3VTSJXBKw2DBjfaJt4eS1X:3:CL:685:TAG')
    res3 = json.dumps(
        await get_revoc_reg_def_helper(
            pool_handle, wallet_handle, submitter_did,
            'RgTvEeKFSxd2Fcsxh42k9T:4:RgTvEeKFSxd2Fcsxh42k9T:3:CL:689:cred_def_tag:CL_ACCUM:revoc_def_tag'))
    res4 = json.dumps(
        await get_revoc_reg_helper(
            pool_handle, wallet_handle, submitter_did,
            'RgTvEeKFSxd2Fcsxh42k9T:4:RgTvEeKFSxd2Fcsxh42k9T:3:CL:689:cred_def_tag:CL_ACCUM:revoc_def_tag',
            timestamp0))
    res5 = json.dumps(
        await get_revoc_reg_delta_helper(
            pool_handle, wallet_handle, submitter_did,
            'RgTvEeKFSxd2Fcsxh42k9T:4:RgTvEeKFSxd2Fcsxh42k9T:3:CL:689:cred_def_tag:CL_ACCUM:revoc_def_tag',
            timestamp0, timestamp1))

    with pytest.raises(IndyError, match='LedgerNotFound'):
        await ledger.parse_get_schema_response(res1)

    with pytest.raises(IndyError, match='LedgerNotFound'):
        await ledger.parse_get_cred_def_response(res2)

    with pytest.raises(IndyError, match='LedgerNotFound'):
        await ledger.parse_get_revoc_reg_def_response(res3)

    with pytest.raises(IndyError, match='LedgerNotFound'):
        await ledger.parse_get_revoc_reg_response(res4)

    with pytest.raises(IndyError, match='LedgerNotFound'):
        await ledger.parse_get_revoc_reg_delta_response(res5)


@pytest.mark.asyncio
async def test_misc_wallet():
    await wallet_helper('abc', 'abc',)
