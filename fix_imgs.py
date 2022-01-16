#!/usr/bin/env python3
# vi: set wm=0 ai sw=4 ts=4 et:

"""
a simple script to input build log information from the command line
"""

import sqlite3 as sql

DBINFO = [{'filename': 'test.sqlite'}]

# used to insert data into the DB in the correct order
ORDER = ['activity', 'hours', 'primary_worker', 'additional_workers',
         'category', 'subcategory', 'cost', 'purchased', 'photo_url']

def main():
    """
    run through the questions
    """
    dbs = setup_dbs()
    fix_images(dbs)
    #save_answers(dbs, answers)
    cleanup_dbs(dbs)


def setup_dbs():
    """
    set up and return a link to the db
    """
    dbs = []
    for db_info in DBINFO:
        dbs.append(sql.connect(db_info['filename']))
    return dbs


def cleanup_dbs(dbs):
    """
    clean up the DB connection
    """
    for db in dbs:
        db.close()


def fix_images(dbs):
    """ modify all entries which have an upper-case IMG or JPG in them """
    for db in dbs:
        cursor = db.cursor()
        query = ('select date, photo_url from events where photo_url '
                 'like "%IMG%"')
        cursor.execute(query)
        entries = cursor.fetchall()
        for entry in entries:
            date, url = entry
            url = url.replace('IMG', 'img')
            url = url.replace('JPG', 'jpg')
            query = (f'update events set photo_url = "{url}" '
                     f'where date = "{date}"')
            print(f'running: {query}')
            cursor.execute(query)
        db.commit()

def save_answers(dbs, answers):
    """
    take the answers entered and insert them into the db
    """
    for db in dbs:
        cursor = db.cursor()
        query = 'insert into events values ({})'
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        arglist = ['"{}"'.format(now)]
        for label in ORDER:
            answer = answers[label]
            try:
                answer = answer.replace('"', '""')
                arglist.append('"{}"'.format(answer))
            except TypeError as err:
                print('got error {} trying to operate on {}'.format(err, answer))
        argstring = ','.join(arglist)
        query = query.format(argstring)
        print('Writing data to sqlite database')
        cursor.execute(query)
        db.commit()
        print('Finished')


if __name__ == '__main__':
    main()
