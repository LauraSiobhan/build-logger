#!/usr/bin/env python3

"""
go through the jpg files in the current directory, and make
thumbnail-size versions of them.
"""

import os
import subprocess

def get_files():
    """ get filenames we can ensmallen from the current directory """
    dirname = '.'
    filenames = os.listdir(dirname)
    files = [filename for filename in filenames 
             if filename.lower().endswith('.jpg') and 
             filename.find('-md') == -1 and
             filename.find('-sm') == -1]
    return files


def ensmallen(filename):
    """ make a given JPG smaller """
    name = '.'.join(filename.split('.')[:-1])
    smallname = name + '-sm.jpg'
    try:
        open(smallname)
    except FileNotFoundError:
        size = get_size(filename)
        cmd = ['convert', '-geometry', size, filename, smallname]
        subprocess.call(cmd)
        print(' '.join(cmd))
        autorot(filename)


def get_size(filename):
    """ use jhead to figure out whether this is a portrait or landscape,
    and return the corresponding size string """

    small_size = '160'

    jhead_info = subprocess.check_output(['jhead', '-c', filename])
    size = str(jhead_info).split(' ')[1]
    edges = size.split('x')
    if edges[0] > edges[1]:
        # is landscape
        return small_size + 'x'
    else:
        return 'x' + small_size


def autorot(filename):
    """ use jhead to autorotate an image """
    cmd = ['jhead', '-autorot', filename]
    subprocess.call(cmd)
    print(' '.join(cmd))


def main():
    filenames = get_files()
    for filename in filenames:
        ensmallen(filename)


if __name__ == '__main__':
    main()
