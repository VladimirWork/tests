import pytest
import os
import subprocess
import testinfra


def test_libindy():
    indy_plenum_ver = '1.6.57'
    indy_anoncreds_ver = '1.0.11'
    indy_node_ver = '1.6.82'
    indy_sdk_deb_path = 'https://repo.sovrin.org/sdk/lib/apt/xenial/rc/'
    indy_sdk_deb_ver = 'libindy_1.7.0~46_amd64.deb'
    os.chdir('/home/indy/indy-sdk')
    subprocess.check_call(['git', 'fetch'])
    subprocess.check_call(['git', 'stash'])
    subprocess.check_call(['git', 'checkout', 'origin/rc'])
    subprocess.check_call(['sed', '-i', '22c\\ARG indy_stream=rc', './ci/indy-pool.dockerfile'])
    subprocess.check_call(['sed', '-i', '27c\\ARG indy_plenum_ver='+indy_plenum_ver, './ci/indy-pool.dockerfile'])
    subprocess.check_call(['sed', '-i', '28c\\ARG indy_anoncreds_ver='+indy_anoncreds_ver, './ci/indy-pool.dockerfile'])
    subprocess.check_call(['sed', '-i', '29c\\ARG indy_node_ver='+indy_node_ver, './ci/indy-pool.dockerfile'])
    subprocess.check_call(['docker', 'build', '-f', 'ci/indy-pool.dockerfile', '-t', 'indy_pool', '.'])
    pool_id = subprocess.check_output(['docker', 'run', '-itd', '-p', '9701-9709:9701-9709', 'indy_pool'])
    subprocess.check_call(['docker', 'build', '--build-arg', 'indy_sdk_deb='+indy_sdk_deb_path+indy_sdk_deb_ver, '-f',
                           'ci/acceptance/ubuntu_acceptance.dockerfile', '.'])
    client_id = subprocess.check_output(['docker', 'run', '-it', '-v', '/home/indy/indy-sdk/samples:/home/indy/samples',
                                         '--network=host', pool_id])
    host = testinfra.get_host("docker://" + client_id)
