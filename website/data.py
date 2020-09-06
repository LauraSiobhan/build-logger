#!/usr/bin/python3

import sqlite3 as sql
import json
import os

def parse_args():
    query = str(os.environ['QUERY_STRING'])
    queries = {}
    for item in query.split('&'):
        q, a = item.split('=')
        queries[q] = a
    return queries


def get_events(cursor, queries):
    offset = int(queries['pagenum']) * int(queries['pagesize'])
    query = "select * from events order by date desc limit {} offset {}"
    cursor.execute(query.format(queries['pagesize'], offset))
    return cursor.fetchall()


def get_total_hours(cursor):
    query = 'select sum(hours) from events'
    cursor.execute(query)
    return cursor.fetchall()


def print_data(data):
    stuff = json.dumps(data)
    print("Content-type: application/json\n\n")
    print(stuff)


def main():
    filename = 'charger-buildlog.sqlite'
    db = sql.connect(filename)
    cursor = db.cursor()

    queries = parse_args()
    data = {}
    data['events'] = get_events(cursor, queries)
    data['total_hours'] = get_total_hours(cursor)
    print_data(data)

if __name__ == '__main__':
    main()
