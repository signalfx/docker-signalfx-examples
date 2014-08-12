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
while True:
    time.sleep(1)
    execute(['curl', 'localhost:83'], expected_code=0)

