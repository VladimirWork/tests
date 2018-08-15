from indy import pool, wallet
import random
import string
import json
import time
import pytest


@pytest.mark.asyncio
async def test_key_derivation_algorithm():
    await pool.set_protocol_version(2)
    config_mod = json.dumps({"id": ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))})
    credentials_mod = json.dumps({"key": '', "key_derivation_method": 'ARAGON2I_MOD'})
    t1_start = float(time.time())
    await wallet.create_wallet(config_mod, credentials_mod)
    t1_create_delta = float(time.time()) - t1_start
    handle_mod = await wallet.open_wallet(config_mod, credentials_mod)
    t1_open_delta = float(time.time()) - t1_start - t1_create_delta
    await wallet.close_wallet(handle_mod)
    t1_close_delta = float(time.time()) - t1_start - t1_create_delta - t1_open_delta
    await wallet.delete_wallet(config_mod, credentials_mod)
    t1_delete_delta = float(time.time()) - t1_start - t1_create_delta - t1_open_delta - t1_close_delta
    print('\n', t1_create_delta, '\n', t1_open_delta, '\n', t1_close_delta, '\n', t1_delete_delta)

    config_int = json.dumps({"id": ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))})
    credentials_int = json.dumps({"key": '', "key_derivation_method": 'ARAGON2I_INT'})
    t2_start = float(time.time())
    await wallet.create_wallet(config_int, credentials_int)
    t2_create_delta = float(time.time()) - t2_start
    handle_int = await wallet.open_wallet(config_int, credentials_int)
    t2_open_delta = float(time.time()) - t2_start - t2_create_delta
    await wallet.close_wallet(handle_int)
    t2_close_delta = float(time.time()) - t2_start - t2_create_delta - t2_open_delta
    await wallet.delete_wallet(config_int, credentials_int)
    t2_delete_delta = float(time.time()) - t2_start - t2_create_delta - t2_open_delta - t2_close_delta
    print('\n', t2_create_delta, '\n', t2_open_delta, '\n', t2_close_delta, '\n', t2_delete_delta)

    assert(t2_create_delta < t1_create_delta)
    assert(t2_open_delta < t1_open_delta)
    assert(t2_delete_delta < t1_delete_delta)
