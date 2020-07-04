import sqlite3 as sql

db = sql.connect('charger-buildlog.sqlite')
c = db.cursor()
query = 'select date from events limit 1'
c.execute(query)
print(c.fetchone())
