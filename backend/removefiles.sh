#!/bin/bash
# This script removes all files from bot folder

# read args
path=$1

# check if exist this directory
if ! [ -d $path ]; then
    echo "This directory does not exist"
    rm $log_file
    exit 1
fi

# remove folder
echo "Removing bot directory..."
rm -rfv $path

echo "Done"
exit 0
