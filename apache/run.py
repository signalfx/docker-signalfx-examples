#!/usr/bin/env python
import threading
import logging
import sys
from dockercommon import execute, fix_collectd_file, fix_signalfx_collectd_file, repeated_http_get

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

fix_signalfx_collectd_file()
fix_collectd_file()
execute(["service", "apache2", "start"], expected_code=0)
execute(["service", "collectd", "start"], expected_code=0)
threads = [
    threading.Thread(target=repeated_http_get, args=("/index.html", .1, 80)),
    threading.Thread(target=repeated_http_get, args=("/nothere", .2, 80))
]
[t.start() for t in threads]
[t.join() for t in threads if t is not None and t.isAlive()]
