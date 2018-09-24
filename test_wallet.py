import time
import pytest
from utils import *
from indy import wallet
import os


@pytest.mark.parametrize('wallet_config, wallet_credentials', [
    (json.dumps({"id": random_string(1)}),
     json.dumps({"key": random_string(100), "key_derivation_method": 'ARGON2I_MOD'})),
    (json.dumps({"id": random_string(100)}),
     json.dumps({"key": random_string(1), "key_derivation_method": 'ARGON2I_INT'}))
])
@pytest.mark.asyncio
async def test_wallet_create_open_positive(wallet_config, wallet_credentials):
    res1 = await wallet.create_wallet(wallet_config, wallet_credentials)
    res2 = await wallet.open_wallet(wallet_config, wallet_credentials)

    assert res1 is None
    assert isinstance(res2, int)


@pytest.mark.asyncio
async def test_wallet_close_delete_positive():
    wallet_handle, wallet_config, wallet_credentials = await wallet_helper()
    res1 = await wallet.close_wallet(wallet_handle)
    res2 = await wallet.delete_wallet(wallet_config, wallet_credentials)

    assert res1 is None
    assert res2 is None


@pytest.mark.parametrize('exp_config, imp_config', [
    (json.dumps({'path': './wallet', 'key': '', 'key_derivation_method': 'ARGON2I_MOD'}),
     json.dumps({'path': './wallet', 'key': ''}))
])
@pytest.mark.asyncio
async def test_wallet_export_import_positive(exp_config, imp_config):
    wallet_handle, wallet_config, wallet_credential = await wallet_helper()
    res1 = await wallet.export_wallet(wallet_handle, exp_config)
    await wallet_destructor(wallet_handle, wallet_config, wallet_credential)
    res2 = await wallet.import_wallet(wallet_config, wallet_credential, imp_config)
    os.remove('./wallet')

    assert res1 is None
    assert res2 is None


@pytest.mark.asyncio
async def test_generate_wallet_key_positive():
    pass
# ---------------------


@pytest.mark.asyncio
async def test_wallet_create_open_negative():
    pass


@pytest.mark.asyncio
async def test_wallet_close_delete_negative():
    pass


@pytest.mark.asyncio
async def test_wallet_export_import_negative():
    pass


@pytest.mark.asyncio
async def test_generate_wallet_key_negative():
    pass
# ---------------------


@pytest.mark.asyncio
async def test_key_derivation_algorithm():
    await pool.set_protocol_version(2)
    config_mod = json.dumps({"id": ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))})
    credentials_mod = json.dumps({"key": '', "key_derivation_method": 'ARGON2I_MOD'})
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
    credentials_int = json.dumps({"key": '', "key_derivation_method": 'ARGON2I_INT'})
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


@pytest.mark.parametrize('seed', [None, '', '0000000000000000000000000000seed'])
@pytest.mark.asyncio
async def test_generate_wallet_key(seed):
    await pool.set_protocol_version(2)
    if not seed:
        key_config = None
    else:
        key_config = json.dumps({'seed': seed})
    wk = await wallet.generate_wallet_key(key_config)
    wallet_handle, wallet_config, wallet_credential = await wallet_helper(None, wk, 'RAW')
    print('\n', wk)
    await wallet_destructor(wallet_handle, wallet_config, wallet_credential)

    assert wk is not None
