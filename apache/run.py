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

#execute(['/usr/sbin/apache2', '-D', 'FOREGROUND'], expected_code=0)
execute(['/usr/sbin/apache2'], expected_code=0)

def update_plugin_hostname(config_filename, hostname):
    with open(config_filename, 'r') as conf:
        contents = conf.read()
    contents = contents.replace("%%%HOSTNAME%%%", hostname)
    with open(config_filename, 'w') as conf:
        conf.write(contents)

def update_plugin_config(config_filename, username, org, password, sendto, auth_token_finder):
    assert(auth_token_finder is not None)
    assert(sendto is not None)
    assert(config_filename is not None)
    assert(username is not None)
    assert(org is not None)
    assert(password is not None)
    execute(['touch', auth_token_finder], expected_code=0)
    (auth_token, stder, retcode) = execute(['python', auth_token_finder, '--org', org, '--password', password, '--url', sendto, username], expected_code=0)
    logger.info("Using auth token %s", auth_token)
    with open(config_filename, 'r') as conf:
        contents = conf.read()
    if '%%%API_HOST%%%' not in contents:
        raise Exception("I expected %%%API_HOST%%% in contents!")
    contents = contents.replace("%%%API_HOST%%%", sendto)
    contents = contents.replace("%%%API_TOKEN%%%", auth_token)
    with open(config_filename, 'w') as conf:
        conf.write(contents)

update_plugin_config('/etc/collectd.d/unmanaged_config/collectd-signalfx.conf', os.getenv('SF_AUTH_USERNAME'), os.getenv('SF_AUTH_ORG'), os.getenv('SF_AUTH_PASSWORD'), os.getenv('SF_AUTH_URL'), '/opt/collectd-signalfx/get_all_auth_tokens.py')
update_plugin_hostname('/etc/collectd/collectd.conf', get_service_name() + '.' + get_container_name())
execute(["service", "collectd", "start"], expected_code=0)

while True:
    time.sleep(1)
    execute(['curl', 'localhost:83'], expected_code=0)

