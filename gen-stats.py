#!/usr/bin/env python3

"""
to start with, find out what the average 30-day work per day number is.  run
through each day with a sliding 30-day window, and calculate the hours per day
for that window.  average that and report it, saving out notable highs and
lows.  this means that there will be (total day - 30) number of windows
examined.
"""

import json
from datetime import date
import queue

def get_data(filename: str) -> dict:
    """ retrieve the statistics data """
    with open(filename, 'r') as fstream:
        data = json.load(fstream)
    return data


def figure_averages(data: dict) -> dict:
    """ go through the data and calculate the 30-day averages """
    highest_avg = 0
    lowest_avg = 10000
    win_begin = date(1, 1, 1)
    num_windows = 0
    window = queue.Queue(30)

    for item in data:
        thisdate = item[0].split(' ')[0]
        thisyear, thismonth, thisday = thisdate.split('-')
        thisdateobj = date(thisyear, thismonth, thisday)
        hours = item[2]

        if (thisdateobj - win_begin).days < 30:
            window.put(hours)
           # todo: deal with this later, it's not interesting enough right now.
