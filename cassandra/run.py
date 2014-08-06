#!/usr/bin/env python
import os
import time
import logging
import sys
import subprocess
import threading
import httplib
import random
from subprocess import PIPE
from maestro.guestutils import get_service_name, get_container_name, get_port
from cassandra.cluster import Cluster

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

cqlsh = '/usr/bin/cqlsh'
cluster = Cluster()

class ExecuteError(Exception):
    pass

def execute(cmd, expected_code=None, stdin=None, background=False):
    logger.debug("Executing %s", cmd)
    proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    if background:
        return ('', '', 0) # In background
    stdout, stderr = proc.communicate(stdin)
    logger.debug("Result (%s, %s, %d)", stdout, stderr, proc.returncode)
    ret = (stdout, stderr, proc.returncode)
    if expected_code is not None and expected_code != ret[2]:
        raise ExecuteError("Unable to execute command %s, result %s/%s/%d", ret[0], ret[1], ret[2])
    return ret

def init():
    session = cluster.connect()
    session.execute("CREATE KEYSPACE test WITH REPLICATION =  {'class': 'SimpleStrategy', 'replication_factor': 1}")
    session.execute("CREATE TABLE test.test_table ( id int, test_value text, PRIMARY KEY (id))")

def insert(session):
    val = random.randint(0, 1000)
    session.execute("INSERT INTO test_table (id, test_value) VALUES (%s, 'test')", (val,))

def truncate(session):
    session.execute("TRUNCATE test_table")

def select(session):
    rows = session.execute("SELECT id FROM test_table LIMIT 1")
    ignored_iteration = 0
    for row in rows:
        ignored_iteration += 1

def remove_single_item(session):
    rows = session.execute("SELECT id FROM test_table LIMIT 1")
    if len(rows) == 0:
        return
    id_key = int(rows[0].id)
    session.execute("DELETE FROM test_table WHERE id = %s", (id_key,))
     
def repeated_exec(function, delay):
    session = cluster.connect()
    session.set_keyspace('test')
    while True:
        time.sleep(delay)
        function(session)

cassandra_rpc_port = get_port('rpc')
execute(['sed', '-i', '-e', "s/^rpc_port.*/rpc_port: %d/" % cassandra_rpc_port, '/etc/cassandra/cassandra.yaml'], expected_code=0)
execute(['service', 'cassandra', 'start'], expected_code=0)
time.sleep(7)
logger.info("Before init")
init()
logger.info("After init")
time.sleep(.5)
threads = [threading.Thread(target=repeated_exec, args=(insert, .1)), threading.Thread(target=repeated_exec, args=(remove_single_item, .15)), threading.Thread(target=repeated_exec, args=(truncate, 15)), threading.Thread(target=repeated_exec, args=(select, .5))]
[t.start() for t in threads]
[t.join() for t in threads if t is not None and t.isAlive()]
