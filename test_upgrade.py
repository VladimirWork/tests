from utils import *
from indy import did
import pytest
import hashlib
import time
from datetime import datetime, timedelta, timezone
import json
import testinfra


@pytest.mark.asyncio
async def test_pool_upgrade_positive():
    await pool.set_protocol_version(2)
    init_time = -20
    version = '1.6.682'
    name = 'upgrade'+'_'+version+'_'+datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
    action = 'start'
    _sha256 = hashlib.sha256().hexdigest()
    _timeout = 10
    schedule = json.dumps(dict(
        {'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv':
         datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(minutes=init_time), '%Y-%m-%dT%H:%M:%S%z'),
         '8ECVSk179mjsjKRLWiQtssMLgp6EPhWXtaYyStWPSGAb':
         datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(minutes=init_time+5), '%Y-%m-%dT%H:%M:%S%z'),
         'DKVxG2fXXTU8yT5N7hGEbXB3dfdAnYv1JczDUHpmDxya':
         datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(minutes=init_time+10), '%Y-%m-%dT%H:%M:%S%z'),
         '4PS3EDQ3dW1tci1Bp6543CfuuebjFrg36kLAUcskGfaA':
         datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(minutes=init_time+15), '%Y-%m-%dT%H:%M:%S%z')}))
    reinstall = False
    force = True
    # package = 'indy-node'
    pool_handle, _ = await pool_helper()
    wallet_handle, _, _ = await wallet_helper()
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))

    req = await ledger.build_pool_upgrade_request(trustee_did, name, version, action, _sha256, _timeout, schedule, None,
                                                  reinstall, force, None)
    res = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    print(res)

    time.sleep(90)

    hosts = [testinfra.get_host('docker://node' + str(i)) for i in range(1, 5)]
    print(hosts)
    outputs = [host.run('dpkg -l | grep indy-node') for host in hosts]
    print(outputs)
    checks = [output.stdout.find(version) for output in outputs]
    print(checks)
    for check in checks:
        assert check is not -1
