""" this script builds up an empty database.  this is very specific to the
charger buildlog, but shows how to create a new database quickly and easily.

DO NOT run this around an existing database, it may be DESTROYED.  you've
been warned. """

import sqlite3 as sql
import os

filename = 'charger-buildlog.sqlite'
files = os.listdir('.')
if filename in files:
    input(f'{filename} already exists! ^C to cancel, or press enter to '
    'continue')
db = sql.connect(filename)
cursor = db.cursor()

cursor.execute(""" CREATE TABLE `events` (
  `date` datetime,
  `activity` varchar(10000),
  `hours` float,
  `primary_worker` varchar(100),
  `additional_workers` varchar(1000),
  `category` varchar(100),
  `subcategory` varchar(100),
  `cost` float,
  `purchased` varchar(1000),
  `photo_url` varchar(200),
  PRIMARY KEY (`date`)
)""")

cursor.execute("""CREATE TABLE `categories` (
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`name`)
)""")

cursor.execute("""CREATE TABLE `subcategories` (
  `name` varchar(100) NOT NULL,
  `subcategory_of` varchar(100) NOT NULL,
  PRIMARY KEY (`name`, `subcategory_of`)
)""")

db.commit()
db.close()
