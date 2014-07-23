<?php

require "statsd.php";
$link = mysql_connect(":/var/run/mysqld/mysqld.sock", "root", "abcdABCD1.") or die("Unable to connect");
mysql_select_db("lamptest") or die ("Unable to select db");
$time_start = microtime(true);
$res = mysql_query("SELECT COUNT(1) FROM test") or die("Unable to count");
$time_end = microtime(true);
$diff = $time_end - $time_start;
StatsD::timing("php.select.call", $diff * 1000);
StatsD::increment("php.total.call", 1);
StatsD::set("php.endpoints", "select");
StatsD::gauge("php.lastcall", $time_end);
print "I worked?\n" + implode(",", mysql_fetch_row($res)) + "\n";
