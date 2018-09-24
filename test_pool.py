import pytest
from utils import *


@pytest.mark.parametrize('pool_name, pool_config', [
    (random_string(1), json.dumps({'genesis_txn': './aws_genesis'})),
    (random_string(100), json.dumps({'genesis_txn': './docker_genesis'}))
])
@pytest.mark.asyncio
async def test_pool_create_open_refresh_positive(pool_name, pool_config):
    await pool.set_protocol_version(2)
    res1 = await pool.create_pool_ledger_config(pool_name, pool_config)
    print(res1)
    res2 = await pool.open_pool_ledger(pool_name, pool_config)
    print(res2)
    res3 = await pool.refresh_pool_ledger(res2)
    print(res3)

    assert res1 is None
    assert isinstance(res2, int)
    assert res3 is None


@pytest.mark.asyncio
async def test_pool_close_delete_positive():
    await pool.set_protocol_version(2)
    pool_handle, pool_name = await pool_helper()
    res1 = await pool.close_pool_ledger(pool_handle)
    res2 = await pool.delete_pool_ledger_config(pool_name)

    assert res1 is None
    assert res2 is None


# --------------------


async def test_pool_create_open_refresh_negative():
    pass


async def test_pool_close_delete_negative():
    pass
