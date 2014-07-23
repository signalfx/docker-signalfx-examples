<?php

require "statsd.php";
$link = mysql_connect(":/var/run/mysqld/mysqld.sock", "root", "abcdABCD1.") or die("Unable to connect");
mysql_select_db("lamptest") or die ("Unable to select db");
$time_start = microtime(true);
mysql_query("DELETE FROM test") or die ("Unable to delete?");
$time_end = microtime(true);
$diff = $time_end - $time_start;
StatsD::timing("php.delete.call", $diff * 1000);
StatsD::increment("php.total.call", 1);
StatsD::set("php.endpoints", "delete");
StatsD::gauge("php.lastcall", $time_end);
print "I worked?\n";
