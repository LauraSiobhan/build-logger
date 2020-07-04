#!/bin/bash

mysql_host=localhost
mysql_user=reaper
mysql_dbname=charger_buildlog
sqlite3_dbname=charger-buildlog.sqlite

# dump the mysql database to a txt file
mysqldump \
  --skip-create-options \
  --compatible=ansi \
  --skip-extended-insert \
  --compact \
  --single-transaction \
  -h$mysql_host \
  -u$mysql_user \
  -p $mysql_dbname \
  > /tmp/localdb.txt

# remove lines mentioning "PRIMARY KEY" or "KEY"
cat /tmp/localdb.txt \
  | grep -v "PRIMARY KEY" \
  | grep -v KEY \
  > /tmp/localdb.txt.1

# mysqldump leaves trailing commas before closing parentheses  
perl -0pe 's/,\n\)/\)/g' /tmp/localdb.txt.1 > /tmp/localdb.txt.2

# change all \' to ''
sed -e 's/\\'\''/'\'''\''/g' /tmp/localdb.txt.2 > /tmp/localdb.txt.3

if [ -e $sqlite3_dbname ]; then
    mv $sqlite3_dbname $sqlite3_dbname.bak
fi
sqlite3 $sqlite3_dbname < /tmp/localdb.txt.3

