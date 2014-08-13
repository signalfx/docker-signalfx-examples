import logging
import os
import sys
import subprocess
import httplib
import time
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

def repeated_http_get(endpoint, sleep_amount, port):
    while execute_endpoint(endpoint, port):
        time.sleep(random.random() * sleep_amount + sleep_amount)
    logger.info("Done executing?")

def repeated_func(to_exec, args, sleep_amount):
    while to_exec(*args):
        time.sleep(random.random() * sleep_amount + sleep_amount)
    logger.info("Done executing?")


def update_in_file(filename, search_for, replace_with, require=True):
    assert replace_with is not None
    assert search_for is not None
    with open(filename, 'r') as conf:
        contents = conf.read()
    if require and search_for not in contents:
        raise ExecuteError("Unable to find %s in %s" % (search_for, contents))
    contents = contents.replace(str(search_for), str(replace_with))
    with open(filename, 'w') as conf:
        conf.write(contents)

def get_auth_token():
    (username, org, password, sendto) = os.getenv('SF_AUTH_USERNAME'), os.getenv('SF_AUTH_ORG'), os.getenv('SF_AUTH_PASSWORD'), os.getenv('SF_AUTH_URL')
    (auth_token, stder, retcode) = execute(['python', '/opt/collectd-signalfx/get_all_auth_tokens.py', '--org', org, '--password', password, '--url', sendto, username], expected_code=0)
    if retcode != 0:
        raise ExecuteError("Invalid return code %d", retcode)
    return auth_token

def fix_signalfx_collectd_file(collectd_config_file='/etc/collectd.d/unmanaged_config/collectd-signalfx.conf'):
    (username, org, password, sendto) = os.getenv('SF_AUTH_USERNAME'), os.getenv('SF_AUTH_ORG'), os.getenv('SF_AUTH_PASSWORD'), os.getenv('SF_AUTH_URL')
    update_in_file(collectd_config_file, '%%%API_HOST%%%', sendto)
    auth_token = get_auth_token()
    update_in_file(collectd_config_file, '%%%API_TOKEN%%%', auth_token)

def fix_collectd_file():
    update_in_file('/etc/collectd/collectd.conf', '%%%HOSTNAME%%%', get_service_name() + '.' + get_container_name())

