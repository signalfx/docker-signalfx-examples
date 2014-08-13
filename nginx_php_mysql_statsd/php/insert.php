<?php

require "statsd.php";
$link = mysql_connect(":/var/run/mysqld/mysqld.sock", "root", "abcdABCD1.") or die("Unable to connect");
mysql_select_db("lamptest") or die ("Unable to select db");
$time_start = microtime(true);
mysql_query("INSERT INTO test(name) VALUES('bob')") or die ("unable to insert...");
$time_end = microtime(true);
$diff = $time_end - $time_start;
StatsD::timing("php.insert.call", $diff * 1000);
StatsD::increment("php.total.call", 1);
StatsD::set("php.endpoints", "insert");
StatsD::gauge("php.lastcall", $time_end);
print "I worked?\n";
