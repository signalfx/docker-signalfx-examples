#!/usr/bin/env python
import time
import logging
import sys
import threading
from dockercommon import execute, repeated_http_get, join_on_threads, fix_signalfx_collectd_file, fix_collectd_file

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

execute(['touch', '/var/log/sf/start'], expected_code=0)
fix_signalfx_collectd_file()
fix_collectd_file()
execute(['nginx', '-t'], expected_code=0)
execute(["/usr/bin/mysqld_safe"], background=True)
time.sleep(10) # Wait for mysql to start
execute(["mysqladmin", '-u', 'root', 'password', 'abcdABCD1.'], expected_code=0)
execute(['mysql', '-u', 'root', '-pabcdABCD1.'], expected_code=0, stdin="CREATE SCHEMA lamptest")
execute(['mysql', '-u', 'root', '-pabcdABCD1.', 'lamptest'], expected_code=0,stdin='CREATE TABLE test(id INT NOT NULL AUTO_INCREMENT, name VARCHAR(100) NOT NULL, PRIMARY KEY(id))')
execute(["service", 'nginx', 'start'], expected_code=0)
execute(["service", "collectd", "start"], expected_code=0)
execute(["service", "php5-fpm", "start"], expected_code=0)
threads = [threading.Thread(target=repeated_http_get, args=("/select.php", .1, 80)), threading.Thread(target=repeated_http_get, args=("/delete.php", 60, 80)), threading.Thread(target=repeated_http_get, args=("/insert.php", .2, 80))]
for t in threads:
    t.daemon=True
[t.start() for t in threads]
join_on_threads(threads)
print "Done?"
