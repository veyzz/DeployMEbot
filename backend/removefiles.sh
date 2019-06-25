#!/bin/bash
# This script removes all files from bot folder

# read args
bot_id=$1
path=$2

# work with db
bot=$(echo "SELECT * FROM bots WHERE id = $bot_id" | sqlite3 $path/deploymebot.db)
echo "DELETE FROM bots WHERE id = $bot_id" | sqlite3 $path/deploymebot.db

user_id=$(echo $bot | awk -F'|' '{print $5}')
bot_name=$(echo $bot | awk -F'|' '{print $2}')
bot_folder=$path/bots/$user_id/$bot_name
echo $bot_folder

# check if exist this directory
if ! [ -d $bot_folder ]; then
    echo "This directory does not exist"
    exit 1
fi

# remove folder
echo "Removing bot directory..."
rm -rfv $bot_folder

echo "Done"
exit 0
