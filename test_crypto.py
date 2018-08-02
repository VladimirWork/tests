import pytest
import json
from utils import wallet_helper
from indy import pool, did, crypto


@pytest.mark.skip('IS-641')
@pytest.mark.asyncio
async def test_crypto_returns_bytes():
    await pool.set_protocol_version(2)
    wallet_handle = await wallet_helper()
    test_did, test_vk = await did.create_and_store_my_did(wallet_handle, "{}")
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    msg = b'byte message'
    res = await crypto.auth_crypt(wallet_handle, trustee_vk, test_vk, msg)
    print(res)
    assert isinstance(res, bytes)
