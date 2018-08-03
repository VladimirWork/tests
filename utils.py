import json
import string
import random
from indy import pool, wallet, ledger


def run_async_method(method):

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(method())


async def pool_helper(pool_name=None,
                      path_to_genesis='/home/indy/docker_genesis'):
    if not pool_name:
        pool_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    pool_config = json.dumps({"genesis_txn": path_to_genesis})
    await pool.create_pool_ledger_config(pool_name, pool_config)
    pool_handle = await pool.open_pool_ledger(pool_name, pool_config)
    return pool_handle


async def wallet_helper(wallet_id=None,
                        wallet_key=''):
    if not wallet_id:
        wallet_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    wallet_config = json.dumps({"id": wallet_id})
    wallet_credential = json.dumps({"key": wallet_key})
    await wallet.create_wallet(wallet_config, wallet_credential)
    wallet_handle = await wallet.open_wallet(wallet_config, wallet_credential)
    return wallet_handle


async def nym_helper(pool_handle, wallet_handle, submitter_did, target_did,
                     target_vk=None, target_alias=None, target_role=None):
    req = await ledger.build_nym_request(submitter_did, target_did, target_vk, target_alias, target_role)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)
    return res


async def attrib_helper(pool_handle, wallet_handle, submitter_did, target_did, xhash=None, raw=None, enc=None):
    req = await ledger.build_attrib_request(submitter_did, target_did, xhash, raw, enc)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)
    return res


async def schema_helper(pool_handle, wallet_handle, submitter_did, data):
    req = await ledger.build_schema_request(submitter_did, data)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)
    return res


async def cred_def_helper(pool_handle, wallet_handle, submitter_did, data):
    req = await ledger.build_cred_def_request(submitter_did, data)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)
    return res


async def get_nym_helper(pool_handle, wallet_handle, submitter_did, target_did):
    req = await ledger.build_get_nym_request(submitter_did, target_did)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)
    return res


async def get_attrib_helper(pool_handle, wallet_handle, submitter_did, target_did, xhash=None, raw=None, enc=None):
    req = await ledger.build_get_attrib_request(submitter_did, target_did, raw, xhash, enc)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)
    return res


async def get_schema_helper(pool_handle, wallet_handle, submitter_did, id_):
    req = await ledger.build_get_schema_request(submitter_did, id_)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)
    return res


async def get_cred_def_helper(pool_handle, wallet_handle, submitter_did, id_):
    req = await ledger.build_get_cred_def_request(submitter_did, id_)
    res = await ledger.sign_and_submit_request(pool_handle, wallet_handle, submitter_did, req)
    return res
