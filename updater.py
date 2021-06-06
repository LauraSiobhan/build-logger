#!/usr/bin/env python3
# vi: set wm=0 ai sw=4 ts=4 et:

"""
this script will prompt you for information related to a time-based activity;
in this case, building an airplane.  run the program without command line
options.

data is stored in a local sqlite3 database.
"""

import sqlite3 as sql
import os, subprocess
from datetime import datetime
from tempfile import NamedTemporaryFile
import sys

# information on the databases to use.  for local sqlite3, this is just a
# filename, but this variable can contain info for multiple databases.  the
# database functions below will need to be updated to work with database types
# other than sqlite3.
DBINFO = [{'filename': 'charger-buildlog.sqlite'}]

def main():
    """
    ask the user a series of questions, saving the answers in the database
    """
    dbs = setup_dbs()
    date = find_entry(dbs)
    update_entry(dbs, date)
    print(f'updated entry for {date} with edited data in {DBINFO[0]["filename"]}')
    cleanup_dbs(dbs)
    # run a script to push the data out to a server; not required for local
    # use, but handy for the build log website i'm running.
    subprocess.run(['./push.sh'])


def setup_dbs():
    """
    set up and return a link to the db.  this system is capable of writing the
    same data to multiple databases, which is handy when using eg MySQL with a
    local and a remote database.
    """
    dbs = []
    for db_info in DBINFO:
        dbs.append(sql.connect(db_info['filename']))
    return dbs


def cleanup_dbs(dbs):
    """
    clean up the DB connection, once we're done with them
    """
    for db in dbs:
        db.close()


def find_entry(dbs):
    """ show the user a list of entries to choose from, and return the date of
    the chosen entry """
    num_entries = 10
    offset = 0
    db = dbs[0]
    cursor = db.cursor()
    i = 0
    go_on = True
    dates = []
    while go_on:
        query = ('select date, activity from events order by date desc limit '
                 f'{num_entries} offset {offset}')
        cursor.execute(query)
        for item in cursor:
            i += 1
            date = item[0]
            dates.append(date)
            activity = item[1]
            print(f'{str(i).rjust(2)}: {date} {activity[:50]}...')
        print('<CR> for more')
        response = input('Entry number to edit? ')
        try:
            number = int(response)
        except ValueError:
            offset += num_entries
            continue
        return dates[number - 1]
        
    
def update_entry(dbs, date):
    """ now that we have a date, put the whole entry into an editor to be
    fixed """
    myeditor = os.environ.get('EDITOR') or os.environ.get('VISUAL')
    db = dbs[0]
    cursor = db.cursor()
    query = f'select * from events where date = "{date}"'
    cursor.execute(query)
    data = cursor.fetchone()
    with NamedTemporaryFile(mode='w+') as fp:
        for i in range(len(data)):
            name = cursor.description[i][0]
            item = data[i]
            fp.write(f'{name}: {item}\n')
        fp.flush()
        subprocess.run([myeditor, fp.name])
        fp.seek(0)
        answer = fp.read()
    answer = answer.replace('"', '""') # escape quotes
    newdata = answer.split('\n')
    del newdata[-1] # splitting on \n makes an erroneous extra final entry

    updates = []
    for item in newdata:
        name, info = item.split(': ')
        updates.append(f'{name} = "{info}"')
    query = f'update events set {", ".join(updates)} where date = "{date}"'
    print(query)
    cursor.execute(query)
    if cursor.rowcount != 1:
        print('failed to update for some reason')
    db.commit()


def get_category(dbs, category=None):
    """
    display a list of categories to choose from, and return the answer.  if
    the user enters anything that's not a matching value from the list, it
    will be added as a new category.
    """
    categories = find_categories(dbs[0], category)
    i = 1
    for cat in categories:
        print('{}: {}'.format(i, cat))
        i += 1
    answer = input()
    try:
        answer = int(answer)
        answer -= 1
        return categories[answer]
    except ValueError:
        save_new_category(dbs, category, answer)
        return answer


def find_categories(db, category=None):
    """
    return a list of category names.  if the category variable is set, this
    function will retrieve a list of subcategory names under the matching
    category name from the database.
    """
    cursor = db.cursor()
    categories = []
    if category is None:
        query = 'select name from categories'
    else:
        query = 'select name from subcategories where '
        query += 'subcategory_of = "{}"'.format(category)
    cursor.execute(query)
    for item in cursor:
        categories.append(item[0])
    return sorted(categories)


def save_new_category(dbs, cat, subcat):
    """
    save the new category out to the DB
    """
    for db in dbs:
        if cat is None:
            query = 'insert or ignore into categories values ("{}")'
            query = query.format(subcat)
        else:
            query = 'insert or ignore into subcategories (name, subcategory_of) '
            query += 'values ("{}", "{}")'.format(subcat, cat)
        cursor = db.cursor()
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
                answer = answer.replace('"', '""') # escape quotes for sqlite
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
