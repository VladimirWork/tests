from utils import *
from indy import did
import pytest
import hashlib
from datetime import datetime, timedelta, timezone
import json


@pytest.mark.asyncio
async def test_pool_upgrade_positive():
    await pool.set_protocol_version(2)
    version = '1.6.673'
    name = 'upgrade'+'_'+version+'_'+datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
    action = 'start'
    _sha256 = hashlib.sha256().hexdigest()
    _timeout = 10
    schedule = json.dumps(dict(
        {'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv':
         datetime.strftime(datetime.now(tz=timezone.utc)+timedelta(minutes=5), '%Y-%m-%dT%H:%M:%S%z'),
         '8ECVSk179mjsjKRLWiQtssMLgp6EPhWXtaYyStWPSGAb':
         datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(minutes=10), '%Y-%m-%dT%H:%M:%S%z'),
         'DKVxG2fXXTU8yT5N7hGEbXB3dfdAnYv1JczDUHpmDxya':
         datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(minutes=15), '%Y-%m-%dT%H:%M:%S%z'),
         '4PS3EDQ3dW1tci1Bp6543CfuuebjFrg36kLAUcskGfaA':
         datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(minutes=20), '%Y-%m-%dT%H:%M:%S%z')}))
    reinstall = False
    force = False
    # package = 'indy-node'
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))

    req = await ledger.build_pool_upgrade_request(trustee_did, name, version, action, _sha256, _timeout, schedule, None,
                                                  reinstall, force, None)
    res = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))

    print(res)
