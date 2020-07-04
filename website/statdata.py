#!/usr/bin/python3

filename = 'stats.json'
with open(filename) as fp:
    stuff = fp.read()
print("Content-type: application/json\n\n")
print(stuff)
