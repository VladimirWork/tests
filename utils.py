import json
import string
import random
from indy import pool, wallet, ledger


async def pool_helper(pool_name=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)),
                      path_to_genesis='/home/indy/docker_genesis'):
    pool_config = json.dumps({"genesis_txn": path_to_genesis})
    await pool.create_pool_ledger_config(pool_name, pool_config)
    pool_handle = await pool.open_pool_ledger(pool_name, pool_config)
    return pool_handle


async def wallet_helper(wallet_id=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5)),
                        wallet_key=''):
    wallet_config = json.dumps({"id": wallet_id})
    wallet_credential = json.dumps({"key": wallet_key})
    await wallet.create_wallet(wallet_config, wallet_credential)
    wallet_handle = await wallet.open_wallet(wallet_config, wallet_credential)
    return wallet_handle


async def nym_helper(pool_handle, wallet_handle, submitter_did, target_did,
                     target_vk=None, target_alias=None, target_role=None):
    req = await ledger.build_nym_request(submitter_did, target_did, target_vk, target_alias, target_role)
    await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)


async def attrib_helper():
    pass


async def schema_helper():
    pass


async def cred_def_helper():
    pass


async def get_nym_helper():
    pass


async def get_attrib_helper():
    pass


async def get_schema_helper():
    pass


async def get_cred_def_helper():
    pass
