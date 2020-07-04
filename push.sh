#!/bin/sh

echo Generating JSON data
./json-showlog.py
echo Uploading data
scp data.json stats.json obairlann.net:.html/aviation/biplane/buildlog/
echo Ensmallening new images
ssh obairlann.net "(cd .html/aviation/biplane/buildlog/images && ./ensmallen.py)"

