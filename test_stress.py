from utils import *
from indy import pool
import time
from concurrent.futures import ProcessPoolExecutor


def test_pool_connections():
    run_async_method(pool.set_protocol_version, 2)
    with ProcessPoolExecutor(25) as e:
        for i in range(25):
            e.submit(run_async_method(pool_helper))
    time.sleep(5)
    assert True
