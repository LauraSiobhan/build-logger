#!/bin/sh

DIR="buildlog"
FILES="index.html table.js dashboard.js dashboard-total.js statdata.py data.py dashboard.html"

scp $FILES obairlann.net:.html/aviation/biplane/$DIR/
scp ensmallen.py obairlann.net:.html/aviation/biplane/$DIR/images/
