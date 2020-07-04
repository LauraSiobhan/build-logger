#!/usr/bin/python3

import sqlite3 as sql
import json

filename = 'charger-buildlog.sqlite'
db = sql.connect(filename)
cursor = db.cursor()
cursor.execute("select * from events where date > '2020-01-01' order "
               "by date desc")
stuff = json.dumps(cursor.fetchall())
print("Content-type: application/json\n\n")
print(stuff)
