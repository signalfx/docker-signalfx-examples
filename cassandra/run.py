#!/usr/bin/env python
import time
import logging
import sys
import threading
import random

from cassandra.cluster import Cluster
from dockercommon import execute, repeated_func, fix_signalfx_collectd_file, fix_collectd_file


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

cqlsh = '/usr/bin/cqlsh'


def init():
    session = cluster.connect()
    session.execute(
        "CREATE KEYSPACE test WITH REPLICATION =  {'class': 'SimpleStrategy', 'replication_factor': 1}")
    session.execute("CREATE TABLE test.test_table ( id int, test_value text, PRIMARY KEY (id))")


def insert(session):
    val = random.randint(0, 1000)
    session.execute("INSERT INTO test_table (id, test_value) VALUES (%s, 'test')", (val,))
    return True


def truncate(session):
    session.execute("TRUNCATE test_table")
    return True


def select(session):
    rows = session.execute("SELECT id FROM test_table LIMIT 1")
    ignored_iteration = 0
    for row in rows:
        ignored_iteration += 1
    return True


def remove_single_item(session):
    rows = session.execute("SELECT id FROM test_table LIMIT 1")
    if len(rows) == 0:
        return True
    id_key = int(rows[0].id)
    session.execute("DELETE FROM test_table WHERE id = %s", (id_key,))
    return True

fix_signalfx_collectd_file()
fix_collectd_file()
execute(["service", "collectd", "start"], expected_code=0)
execute(['service', 'cassandra', 'start'], expected_code=0)
time.sleep(7)
logger.info("Before init")
cluster = Cluster()
init()
logger.info("After init")
time.sleep(.5)
threads = [threading.Thread(target=repeated_func, args=(insert, [cluster.connect('test')], .1)),
           threading.Thread(target=repeated_func, args=(remove_single_item, [cluster.connect('test')], .15)),
           threading.Thread(target=repeated_func, args=(truncate, [cluster.connect('test')], 15)),
           threading.Thread(target=repeated_func, args=(select, [cluster.connect('test')], .5))]
[t.start() for t in threads]
[t.join() for t in threads if t is not None and t.isAlive()]
