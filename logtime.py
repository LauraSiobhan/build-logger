#!/usr/bin/env python3
# vi: set wm=0 ai sw=4 ts=4 et:

"""
a simple script to input build log information from the command line
"""

import sqlite3 as sql
import os, subprocess
from datetime import datetime
from tempfile import NamedTemporaryFile

# TODO: add readline support

DBINFO = [{'filename': 'charger-buildlog.sqlite'}]

QUESTIONS = {'category': 'Select or Enter Category',
             'subcategory': 'Select or Enter Subcategory',
             'activity': 'What activity',
             'hours': 'How many hours (decimal)',
             'primary_worker': 'Who was the primary worker [<CR> for Ian]',
             'additional_workers': 'Any additional workers',
             'photo_url': 'What photo URL',
             'cost': 'Any cost associated (dollars)',
             'purchased': 'What was purchased'}

# used to insert data into the DB in the correct order
ORDER = ['activity', 'hours', 'primary_worker', 'additional_workers',
         'category', 'subcategory', 'cost', 'purchased', 'photo_url']

def main():
    """
    run through the questions
    """
    dbs = setup_dbs()
    answers = get_answers(dbs)
    save_answers(dbs, answers)
    cleanup_dbs(dbs)
    subprocess.run(['./push.sh'])


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


def get_answers(dbs):
    """
    ask the various questions
    """
    local_order = ORDER[:]
    local_order.remove('category')
    local_order.remove('subcategory')
    answers = {}
    print(QUESTIONS['category'])
    answers['category'] = get_category(dbs)
    print(QUESTIONS['subcategory'])
    answers['subcategory'] = get_category(dbs, answers['category'])
    for label in local_order:
        question = QUESTIONS[label]
        answers[label] = ask_question(question)
        if label == 'cost' and answers[label] == '':
            answers[label] = '0'
        elif label == 'primary_worker' and answers[label] == '':
            answers[label] = 'Ian'
    return answers


def get_category(dbs, category=None):
    """
    display a list of categories to choose from, and return the answer
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
    will pick a category when given no arg, but will pick a subcat
    if given an arg of category name
    returns a list of names
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
    ask a generic question
    """
    answer = input(question + ' (:e for editor): ')
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
                answer = answer.replace('"', '\\"')
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
