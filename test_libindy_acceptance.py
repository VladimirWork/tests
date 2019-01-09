import pytest
import os
import subprocess


def test_libindy():
    indy_plenum_ver = '1.6.57'
    indy_anoncreds_ver = '1.0.11'
    indy_node_ver = '1.6.82'
    os.chdir('/home/indy/indy-sdk')
    subprocess.check_call(['git', 'fetch'])
    subprocess.check_call(['git', 'stash'])
    subprocess.check_call(['git', 'checkout', 'origin/rc'])
    subprocess.check_call(['sed', '-i', '22c\\ARG indy_stream=rc', './ci/indy-pool.dockerfile'])
    subprocess.check_call(['sed', '-i', '27c\\ARG indy_plenum_ver='+indy_plenum_ver, './ci/indy-pool.dockerfile'])
    subprocess.check_call(['sed', '-i', '28c\\ARG indy_anoncreds_ver='+indy_anoncreds_ver, './ci/indy-pool.dockerfile'])
    subprocess.check_call(['sed', '-i', '29c\\ARG indy_node_ver='+indy_node_ver, './ci/indy-pool.dockerfile'])
