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

# information on the databases to use.  for local sqlite3, this is just a
# filename, but this variable can contain info for multiple databases.  the
# database functions below will need to be updated to work with database types
# other than sqlite3.
DBINFO = [{'filename': 'charger-buildlog.sqlite'}]

# questions to ask the user.  the key is the db column name, and the value is
# the text to show the user.
QUESTIONS = {'category': 'Select or Enter Category',
             'subcategory': 'Select or Enter Subcategory',
             'activity': 'What activity',
             'hours': 'How many hours (decimal)',
             'primary_worker': 'Who was the primary worker [<CR> for Laura]',
             'additional_workers': 'Any additional workers',
             'photo_url': 'What photo URL',
             'cost': 'Any cost associated (dollars)',
             'purchased': 'What was purchased'}

# system defaults
DEFAULT_COST = '0'
DEFAULT_WORKER = 'Laura'

# used to insert data into the DB in the correct order.  this should be
# updated to match your DB schema.
ORDER = ['activity', 'hours', 'primary_worker', 'additional_workers',
         'category', 'subcategory', 'cost', 'purchased', 'photo_url']

def main():
    """
    ask the user a series of questions, saving the answers in the database
    """
    dbs = setup_dbs()
    answers = get_answers(dbs)
    save_answers(dbs, answers)
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


def get_answers(dbs):
    """
    print questions for the user, and record answers
    """
    answers = {}
    local_order = ORDER[:]

    # category and subcategory are handled by the get_category() function,
    # since they are built to automatically add new categories if the user
    # doesn't pick one of the existing choices.
    local_order.remove('category')
    local_order.remove('subcategory')

    print(QUESTIONS['category'])
    answers['category'] = get_category(dbs)
    print(QUESTIONS['subcategory'])
    answers['subcategory'] = get_category(dbs, answers['category'])

    # now ask the simpler questions
    for label in local_order:
        question = QUESTIONS[label]
        answers[label] = ask_question(question)

        # this section adds default answers, if the user enters no data, but a
        # value needs to be present
        if answers[label] == '':
            if label == 'cost':
                answers[label] = DEFAULT_COST
            elif label == 'primary_worker':
                answers[label] = DEFAULT_WORKER
    return answers


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


def ask_question(question):
    """
    ask a generic question, and return the answer
    """
    answer = input(question + ' (:e for editor): ')
    # if the user specifies :e as their answer, attempt to start an editor
    # such as vi or emacs, to allow for more complex entries
    if answer == ':e':
        myeditor = os.environ.get('EDITOR') or os.environ.get('VISUAL')
        with NamedTemporaryFile(mode='w+') as fp:
            subprocess.run([myeditor, fp.name])
            answer = fp.read().strip()
            print('retrieved answer: {}'.format(answer))
    return answer


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
