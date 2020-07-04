#!/bin/sh

echo Uploading data
scp charger-buildlog.sqlite obairlann.net:.html/aviation/biplane/buildlog/
echo Ensmallening new images
ssh obairlann.net "(cd .html/aviation/biplane/buildlog/images && ./ensmallen.py)"

