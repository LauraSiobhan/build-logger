#!/usr/bin/env python3
# vi: set wm=0 ai sw=4 ts=4 et:

"""
a simple script to input build log information from the command line
"""

import mysql.connector as dbcon
import os, subprocess
from tempfile import NamedTemporaryFile

# TODO: add readline support

DBINFO = {'user': 'reaper', 'password': 'hello*', 'database': 'buildlog'}

QUESTIONS = {'category': 'Select or Enter Category',
             'subcategory': 'Select or Enter Subcategory',
             'activity': 'What activity',
             'hours': 'How many hours (decimal)',
             'primary_worker': 'Who was the primary worker',
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
    db = setup_db()
    answers = get_answers(db)
    save_answers(db, answers)
    cleanup_db(db)


def setup_db():
    """
    set up and return a link to the db
    """
    db = dbcon.connect(**DBINFO)
    return db


def cleanup_db(db):
    """
    clean up the DB connection
    """
    db.close()


def get_answers(db):
    """
    ask the various questions
    """
    local_order = []
    for item in ORDER:
        local_order.append(item)
    local_order.remove('category')
    local_order.remove('subcategory')
    answers = {}
    print(QUESTIONS['category'])
    answers['category'] = get_category(db)
    print(QUESTIONS['subcategory'])
    answers['subcategory'] = get_category(db, answers['category'])
    for label in local_order:
        question = QUESTIONS[label]
        answers[label] = ask_question(question)
    return answers


def get_category(db, category=None):
    """
    display a list of categories to choose from, and return the answer
    """
    categories = find_categories(db, category)
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
        save_new_category(db, category, answer)
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


def save_new_category(db, cat, subcat):
    """
    save the new category out to the DB
    """
    if cat is None:
        query = 'insert ignore into categories value ("{}")'
        query = query.format(subcat)
    else:
        query = 'insert ignore into subcategories (name, subcategory_of) '
        query += 'value ("{}", "{}")'.format(subcat, cat)
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()


def ask_question(question):
    """
    ask a generic question
    """
    answer = input(question + ' (:e for editor): ')
    if answer == ':e':
        myfile = NamedTemporaryFile()
        myeditor = os.environ.get('EDITOR') or os.environ.get('VISUAL')
        with NamedTemporaryFile(mode='w+') as fp:
            subprocess.run([myeditor, fp.name])
            answer = fp.read().strip()
            print('retrieved answer: {}'.format(answer))
    return answer


def save_answers(db, answers):
    """
    take the answers entered and insert them into the db
    """
    cursor = db.cursor()
    query = 'insert into events value ({})'
    arglist = ['NOW()']
    for label in ORDER:
        answer = answers[label]
        try:
            answer = answer.replace('"', '\\"')
            arglist.append('"{}"'.format(answer))
        except TypeError as err:
            print('got error {} trying to operate on {}'.format(err, answer))
    argstring = ','.join(arglist)
    query = query.format(argstring)
    print('Writing data to database')
    cursor.execute(query)
    db.commit()
    print('Finished')


if __name__ == '__main__':
    main()
