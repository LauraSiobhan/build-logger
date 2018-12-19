#!/usr/bin/env python3
# vi: set wm=0 ai sw=4 ts=4 et:

"""
"""

import mysql.connector as dbcon
import datetime
import json

ORDER = ['date', 'activity', 'hours', 'primary_worker', 'additional_workers',
         'category', 'subcategory', 'cost', 'purchased', 'photo_url']

DBINFO = {'user': 'marquart', 'password': 'Hello*8there', 'database':
          'charger_buildlog', 'host': 'mysql.marquartcharger.org'}



def main():
    """
    """
    db = setup_db()
    data = get_data(db)
    print_data(data)
    cleanup_db(db)


def print_data(data):
    clean_data = []
    for item in data:
        clean_item = []
        for value in item:
            newvalue = value
            if type(value) not in [str, int, float]:
                newvalue = str(value)
            clean_item.append(newvalue)
        clean_data.append(clean_item)
    print(json.dumps(clean_data))


def setup_db():
    """
    set up and return a link to the db
    """
    db = dbcon.connect(**DBINFO)
    return db


def cleanup_db(db):
    db.close()


def get_data(db):
    """
    connect to the DB and download all the goo
    """
    cursor = db.cursor()
    items = []
    query = 'select * from events'
    cursor.execute(query)
    for item in cursor:
        items.append(item)
    return items

if __name__ == '__main__':
    main()
