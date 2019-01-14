import os
import subprocess
import testinfra


def test_libindy():
    indy_plenum_ver = '1.6.57'
    indy_anoncreds_ver = '1.0.11'
    indy_node_ver = '1.6.82'
    indy_sdk_deb_path = 'https://repo.sovrin.org/sdk/lib/apt/xenial/stable/'
    indy_sdk_deb_ver = 'libindy_1.7.0_amd64.deb'
    indy_sdk_ver = '1.7.0'
    os.chdir('/home/indy/indy-sdk')
    subprocess.check_call(['git', 'stash'])
    subprocess.check_call(['git', 'fetch'])
    subprocess.check_call(['git', 'checkout', 'origin/rc'])
    subprocess.check_call(['sed', '-i', '22c\\ARG indy_stream=rc', './ci/indy-pool.dockerfile'])
    subprocess.check_call(['sed', '-i', '27c\\ARG indy_plenum_ver={}'.format(indy_plenum_ver),
                           './ci/indy-pool.dockerfile'])
    subprocess.check_call(['sed', '-i', '28c\\ARG indy_anoncreds_ver={}'.format(indy_anoncreds_ver),
                           './ci/indy-pool.dockerfile'])
    subprocess.check_call(['sed', '-i', '29c\\ARG indy_node_ver={}'.format(indy_node_ver),
                           './ci/indy-pool.dockerfile'])
    # set version of `indy` dependency in `pom.xml` to libindy version
    subprocess.check_call(['sed', '-i', '112c\\\t\t\t<version>{}</version>'.format(indy_sdk_ver),
                           './samples/java/pom.xml'])
    # set version of `python3-indy` dependency in `setup.py` to libindy version
    subprocess.check_call(['sed', '-i', '11c\\    install_requires=[\'python3-indy=={}\']'.format(indy_sdk_ver),
                           './samples/python/setup.py'])
    subprocess.check_call(['docker', 'build', '-f', 'ci/indy-pool.dockerfile', '-t', 'indy_pool', '.'])
    subprocess.check_call(['docker', 'run', '-itd', '-p', '9701-9709:9701-9709', 'indy_pool'])
    pool_id = subprocess.check_output(['docker', 'build', '--build-arg', 'indy_sdk_deb={}'.
                                       format(indy_sdk_deb_path+indy_sdk_deb_ver), '-f',
                                       'ci/acceptance/ubuntu_acceptance.dockerfile', '.'])[-13:-1].decode().strip()
    print(pool_id)
    client_id = subprocess.check_output(['docker', 'run', '-itd', '-v',
                                         '/home/indy/indy-sdk/samples:/home/indy/samples', '--network=host', pool_id])\
        .decode().strip()
    print(client_id)
    host = testinfra.get_host("docker://{}".format(client_id))

    # test java
    java_res = host.\
        run('cd /home/indy/samples/java && TEST_POOL_IP=127.0.0.1 mvn clean compile exec:java -Dexec.mainClass="Main"')
    host.run('rm -rf /home/indy/.indy_client')
    assert java_res.stdout.find('BUILD SUCCESS') is not -1
    print(java_res)

    # test python
    host.run('cd /home/indy/samples/python && python3.5 -m pip install --user -e .')
    python_res = host.run('cd /home/indy/samples/python && TEST_POOL_IP=127.0.0.1 python3.5 src/main.py')
    host.run('rm -rf /home/indy/.indy_client')
    assert python_res
    print(python_res)