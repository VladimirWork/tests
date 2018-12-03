from utils import *
from indy import did
import pytest
import hashlib
import time
from datetime import datetime, timedelta, timezone
import json
import testinfra
import os


@pytest.mark.asyncio
async def test_pool_upgrade_positive():
    await pool.set_protocol_version(2)
    timestamp0 = int(time.time())
    dests = ['Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv', '8ECVSk179mjsjKRLWiQtssMLgp6EPhWXtaYyStWPSGAb',
             'DKVxG2fXXTU8yT5N7hGEbXB3dfdAnYv1JczDUHpmDxya', '4PS3EDQ3dW1tci1Bp6543CfuuebjFrg36kLAUcskGfaA',
             '4SWokCJWJc69Tn74VvLS6t2G2ucvXqM9FDMsWJjmsUxe', 'Cv1Ehj43DDM5ttNBmC6VPpEfwXWwfGktHwjDJsTV5Fz8',
             'BM8dTooz5uykCbYSAAFwKNkYfT4koomBHsSWHTDtkjhW', '98VysG35LxrutKTNXvhaztPFHnx5u9kHtT7PnUGqDa8x',
             '6pfbFuX5tx7u3XKz8MNK4BJiHxvEcnGRBs1AQyNaiEQL', 'HaNW78ayPK4b8vTggD4smURBZw7icxJpjZvCMLdUueiN',
             '2zUsJuF9suBy2iKkcgmm8uoMB6u5Dq2oHoRuchrZbj2N', 'BXV4SXKEJeYQ8XCRHgpw1Xume5ntqALsRhbUYcF85Mse',
             '71WAtEevzz8aZr8baNJhQCUDLwRhM7LeaErSKNWWKxzn', 'FEUGMFWCSAM725vyH8JZnsitiNUy31NPhugVKb8zDpng',
             'DPZ8GJ1NyNZGJMU6qQZVuBsumY1aVzvcV4FqQK9Y215x', 'FYDoBrDhfGuSwt39Sgd3DZETihpnXy6SzZBggyD9HMrD',
             'EMNhsHNsEpuffxCmgC3fpwVj7LgwtSm3riSizCMN6MBo', 'HD1XnVG6jXqGdmFMDTdJk3AoChxaqTfa6zGLkyXTtHwH',
             'DUGXi5vxRZcrDC8VPZFU6bpiHDMhnWic9tDaoDJv3Bj6', 'D7jphMASPQAD6UFvT2ULjEfYybCJVDzwvfG5ZWJoXa69',
             '7vcRBffPvKuGQz4F1ThYAo3Ucq3rXgU62enf6d23u8KX', 'DfSoxVHbbdZrAmwTJcRqM2arwUSvK3L6PXjqWHGo58xD',
             'FTBmYnhxVd8zXZFRzca5WFKh7taW9J573T8pXEWL8Wbb', 'EjZrHfLTBR38d67HasBxpyKRBvrPBJ5RiAMubPWXLxWr',
             'koKn32jREPYR642DQsFftPoCkTf3XCPcfvc3x9RhRK7'
             ]
    init_time = 1
    version = '1.6.79'
    status = 'Active: active (running)'
    name = 'upgrade'+'_'+version+'_'+datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
    action = 'start'
    _sha256 = hashlib.sha256().hexdigest()
    _timeout = 10
    docker_4_schedule = json.dumps(dict(
        {dest:
            datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(minutes=init_time+i*5), '%Y-%m-%dT%H:%M:%S%z')
         for dest, i in zip(dests[:4], range(len(dests[:4])))}
    ))
    aws_25_schedule = json.dumps(dict(
        {dest:
            datetime.strftime(datetime.now(tz=timezone.utc) + timedelta(minutes=init_time+i*5), '%Y-%m-%dT%H:%M:%S%z')
         for dest, i in zip(dests, range(len(dests)))}
    ))
    reinstall = False
    force = False
    # package = 'indy-node'
    pool_handle, _ = await pool_helper(path_to_genesis='./aws_genesis')
    wallet_handle, _, _ = await wallet_helper()
    random_did = random_did_and_json()[0]
    another_random_did = random_did_and_json()[0]
    trustee_did, trustee_vk = await did.create_and_store_my_did(wallet_handle, json.dumps(
        {'seed': '000000000000000000000000Trustee1'}))

    # add all txns before the upgrade
    nym_before_res = await nym_helper(pool_handle, wallet_handle, trustee_did, random_did)
    attrib_before_res = await attrib_helper(pool_handle, wallet_handle, trustee_did, random_did, None,
                                            json.dumps({'key': 'value'}), None)
    schema_id, schema_before_res = await schema_helper(pool_handle, wallet_handle, trustee_did,
                                                       'schema_name_upgrade_case', '1.0',
                                                       json.dumps(["age", "sex", "height", "name"]))
    temp = await get_schema_helper(pool_handle, wallet_handle, trustee_did, schema_id)
    schema_id, schema_json = await ledger.parse_get_schema_response(json.dumps(temp))

    cred_def_id, _, cred_def_before_res =\
        await cred_def_helper(pool_handle, wallet_handle, trustee_did, schema_json, 'cred_def_tag_upgrade_case', 'CL',
                              json.dumps({'support_revocation': True}))

    revoc_reg_def_id1, _, _, revoc_reg_def_before_res =\
        await revoc_reg_def_helper(pool_handle, wallet_handle, trustee_did, 'CL_ACCUM', 'revoc_def_tag1_upgrade_case',
                                   cred_def_id,
                                   json.dumps({'max_cred_num': 1, 'issuance_type': 'ISSUANCE_BY_DEFAULT'}))

    revoc_reg_def_id2, _, _, revoc_reg_entry_before_res =\
        await revoc_reg_entry_helper(pool_handle, wallet_handle, trustee_did, 'CL_ACCUM', 'revoc_def_tag2_upgrade_case',
                                     cred_def_id,
                                     json.dumps({'max_cred_num': 1, 'issuance_type': 'ISSUANCE_BY_DEFAULT'}))
    timestamp1 = int(time.time())

    # schedule pool upgrade
    req = await ledger.build_pool_upgrade_request(trustee_did, name, version, action, _sha256, _timeout,
                                                  aws_25_schedule, None, reinstall, force, None)
    res = json.loads(await ledger.sign_and_submit_request(pool_handle, wallet_handle, trustee_did, req))
    print(res)

    time.sleep(7700)

    docker_4_hosts = [testinfra.get_host('docker://node' + str(i)) for i in range(1, 5)]
    aws_25_hosts = [testinfra.get_host('ssh://auto_node'+str(i),
                                       ssh_config='/home/indy/indy-node/pool_automation/auto/.ssh/ssh_config')
                    for i in range(1, 26)]
    print(aws_25_hosts)
    os.chdir('/home/indy/indy-node/pool_automation/auto/.ssh/')
    version_outputs = [host.run('dpkg -l | grep indy-node') for host in aws_25_hosts]
    print(version_outputs)
    status_outputs = [host.run('systemctl status indy-node') for host in aws_25_hosts]
    print(status_outputs)
    os.chdir('/home/indy/PycharmProjects/tests')
    version_checks = [output.stdout.find(version) for output in version_outputs]
    print(version_checks)
    status_checks = [output.stdout.find(status) for output in status_outputs]
    print(status_checks)

    # read all txns that were added before the upgrade
    get_nym_after_res = await get_nym_helper(pool_handle, wallet_handle, trustee_did, random_did)
    get_attrib_after_res = await get_attrib_helper(pool_handle, wallet_handle, trustee_did, random_did,
                                                   None, 'key', None)
    get_schema_after_res = await get_schema_helper(pool_handle, wallet_handle, trustee_did, schema_id)
    get_cred_def_after_res = await get_cred_def_helper(pool_handle, wallet_handle, trustee_did, cred_def_id)
    get_revoc_reg_def_after_res =\
        await get_revoc_reg_def_helper(pool_handle, wallet_handle, trustee_did, revoc_reg_def_id1)
    get_revoc_reg_after_res =\
        await get_revoc_reg_helper(pool_handle, wallet_handle, trustee_did, revoc_reg_def_id2, timestamp1)
    get_revoc_reg_delta_after_res =\
        await get_revoc_reg_delta_helper(pool_handle, wallet_handle, trustee_did, revoc_reg_def_id2,
                                         timestamp0, timestamp1)
    add_before_results = [nym_before_res, attrib_before_res, schema_before_res, cred_def_before_res,
                          revoc_reg_def_before_res, revoc_reg_entry_before_res]
    get_after_results = [get_nym_after_res, get_attrib_after_res, get_schema_after_res, get_cred_def_after_res,
                         get_revoc_reg_def_after_res, get_revoc_reg_after_res, get_revoc_reg_delta_after_res]

    for res in add_before_results:
        assert res['op'] == 'REPLY'

    for res in get_after_results:
        assert res['result']['seqNo'] is not None

    for check in version_checks:
        assert check is not -1

    for check in status_checks:
        assert check is not -1
