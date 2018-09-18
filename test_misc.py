import pytest
from indy import pool, did
from utils import *


@pytest.mark.asyncio
async def test_misc():
    await pool.set_protocol_version(2)
    pool_handle = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    submitter_did, submitter_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))
    res1 = json.loads(await get_cred_def_helper(pool_handle, wallet_handle, submitter_did,
                                                '5SRugmRhxMypiQ8iBabAxj:3:CL:17'))
    res2 = json.loads(await get_cred_def_helper(pool_handle, wallet_handle, submitter_did,
                                                'VRaXpAenQy5gK8mNDUdJe8:3:CL:20'))
    print(res1)
    print(res2)
