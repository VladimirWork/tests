import pytest
import json
from utils import wallet_helper
from indy import pool, did, crypto


@pytest.mark.asyncio
async def test_auth_crypt_decrypt():
    await pool.set_protocol_version(2)
    wallet_handle, _, _ = await wallet_helper()
    test_did, test_vk = await did.create_and_store_my_did(wallet_handle, "{}")
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {"seed": str('000000000000000000000000Trustee1')}))
    msg = b'byte message'
    encrypted_message = await crypto.auth_crypt(wallet_handle, trustee_vk, test_vk, msg)
    assert isinstance(encrypted_message, bytes)
    sender_vk, decrypted_message = await crypto.auth_decrypt(wallet_handle, test_vk, encrypted_message)
    assert(sender_vk == trustee_vk)
    assert isinstance(decrypted_message, bytes)
    assert (decrypted_message == msg)


@pytest.mark.asyncio
async def test_anon_crypt_decrypt():
    await pool.set_protocol_version(2)
    wallet_handle, _, _ = await wallet_helper()
    test_did, test_vk = await did.create_and_store_my_did(wallet_handle, "{}")
    msg = b'byte message'
    encrypted_message = await crypto.anon_crypt(test_vk, msg)
    assert isinstance(encrypted_message, bytes)
    decrypted_message = await crypto.anon_decrypt(wallet_handle, test_vk, encrypted_message)
    assert isinstance(decrypted_message, bytes)
    assert (decrypted_message == msg)
