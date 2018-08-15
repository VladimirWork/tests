from utils import *
import time
import pytest


@pytest.mark.asyncio
async def test_key_derivation_algorithm():
    await pool.set_protocol_version(2)
    t1 = float(time.time())
    await wallet_helper()
    t2 = float(time.time())
    await wallet_helper(wallet_key_derivation_method='ARAGON2I_INT')
    t3 = float(time.time())
    assert((t3 - t2) < (t2 - t1))
    print('ARAGON2I_MOD: %f' % (t2 - t1))
    print('ARAGON2I_INT: %f' % (t3 - t2))


@pytest.mark.asyncio
async def test_key_derivation_algorithm_vice_versa():
    await pool.set_protocol_version(2)
    t1 = float(time.time())
    await wallet_helper(wallet_key_derivation_method='ARAGON2I_INT')
    t2 = float(time.time())
    await wallet_helper()
    t3 = float(time.time())
    assert ((t3 - t2) > (t2 - t1))
    print('ARAGON2I_INT: %f' % (t2 - t1))
    print('ARAGON2I_MOD: %f' % (t3 - t2))
