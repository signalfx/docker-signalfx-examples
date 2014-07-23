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

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ExecuteError(Exception):
    pass

def join_on_threads(threads):
    """
    Join with a timeout so we can unblock for a Keyboard interrupt.  See
    http://www.regexprn.com/2010/05/killing-multithreaded-python-programs.html
    """
    logger.debug("Joining threads")
    while len(threads) > 0:
        try:
            # Join all threads using a timeout so it doesn't block
            # Filter out threads which have been joined or are None
            [t.join(1) for t in threads if t is not None and t.isAlive()]
            threads = [t for t in threads if t is not None and t.isAlive()]
        except KeyboardInterrupt:
            return

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

def execute_endpoint(endpoint, port):
    conn = httplib.HTTPConnection("localhost", port=port)
    conn.request("GET", endpoint)
    r1 = conn.getresponse()
    if r1.status != 200:
        return False
    return True

def repeated_execute(endpoint, sleep_amount, port):
    while execute_endpoint(endpoint, port):
        time.sleep(random.random() * sleep_amount + sleep_amount)
    logger.info("Done executing?")

def update_plugin_hostname(config_filename, hostname):
    with open(config_filename, 'r') as conf:
        contents = conf.read()
    contents = contents.replace("%%%HOSTNAME%%%", hostname)
    with open(config_filename, 'w') as conf:
        conf.write(contents)


def update_nginx_host(config_filename, port):
    with open(config_filename, 'r') as conf:
        contents = conf.read()
    if '%%%LISTEN_PORT%%%' not in contents:
        raise Exception("I expected %%%LISTEN_PORT%%% in contents!")
    contents = contents.replace("%%%LISTEN_PORT%%%", str(port))
    with open(config_filename, 'w') as conf:
        conf.write(contents)

def update_plugin_config(config_filename, auth_token, sendto):
    assert(auth_token is not None)
    assert(sendto is not None)
    with open(config_filename, 'r') as conf:
        contents = conf.read()
    if '%%%API_HOST%%%' not in contents:
        raise Exception("I expected %%%API_HOST%%% in contents!")
    contents = contents.replace("%%%API_HOST%%%", sendto)
    contents = contents.replace("%%%API_TOKEN%%%", auth_token)
    with open(config_filename, 'w') as conf:
        conf.write(contents)


execute(['touch', '/var/log/sf/start'], expected_code=0)
update_plugin_config('/etc/collectd.d/unmanaged_config/10-signalfx_plugin.conf', os.getenv('SF_AUTH_TOKEN'), os.getenv('SF_AUTH_HOST'))
update_nginx_host('/etc/nginx/nginx.conf', get_port('http'))
update_nginx_host('/etc/collectd.d/unmanaged_config/10-nginx.conf', get_port('http'))
execute(['nginx', '-t'], expected_code=0)
update_plugin_hostname('/etc/collectd/collectd.conf', get_service_name() + '.' + get_container_name())
execute(["/usr/bin/mysqld_safe"], background=True)
time.sleep(10) # Wait for mysql to start
execute(["mysqladmin", '-u', 'root', 'password', 'abcdABCD1.'], expected_code=0)
execute(['mysql', '-u', 'root', '-pabcdABCD1.'], expected_code=0, stdin="CREATE SCHEMA lamptest")
execute(['mysql', '-u', 'root', '-pabcdABCD1.', 'lamptest'], expected_code=0,stdin='CREATE TABLE test(id INT NOT NULL AUTO_INCREMENT, name VARCHAR(100) NOT NULL, PRIMARY KEY(id))')
execute(["service", 'nginx', 'start'], expected_code=0)
execute(["service", "collectd", "start"], expected_code=0)
execute(["service", "php5-fpm", "start"], expected_code=0)
execute(["nginx", "-t"], expected_code=0)
threads = [threading.Thread(target=repeated_execute, args=("/select.php", .1, get_port('http'))), threading.Thread(target=repeated_execute, args=("/delete.php", 60, get_port('http'))), threading.Thread(target=repeated_execute, args=("/insert.php", .2, get_port('http')))]
for t in threads:
    t.daemon=True
[t.start() for t in threads]
join_on_threads(threads)
print "Done?"
