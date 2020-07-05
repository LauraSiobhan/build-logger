#!/usr/bin/python3

import sqlite3 as sql
import json
import os

query = str(os.environ['QUERY_STRING'])
#query = "pagenum=0&pagesize=1"
queries = {}
for item in query.split('&'):
    q, a = item.split('=')
    queries[q] = a
with open('requests.log', 'a') as fp:
    fp.write('got a request\n')
    fp.write(str(queries))
    fp.write('\n')
filename = 'charger-buildlog.sqlite'
db = sql.connect(filename)
cursor = db.cursor()
offset = int(queries['pagenum']) * int(queries['pagesize'])
query = "select * from events order by date desc limit {} offset {}"
cursor.execute(query.format(queries['pagesize'], offset))
stuff = json.dumps(cursor.fetchall())
print("Content-type: application/json\n\n")
print(stuff)
