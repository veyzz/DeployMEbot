#!/bin/bash
# This script prepare file structure for new user's bot
user_id=$1
arch=$2
pathtobot=$3
bot_name=${arch%.zip}

# make new dir and clean old files
echo $pathtobot/bots/$user_id
mkdir $pathtobot/bots/$user_id
mkdir $pathtobot/bots/$user_id/$bot_name
rm -rf $pathtobot/bots/$user_id/$bot_name/*

# unzip files
unzip $pathtobot/download/$user_id/$arch -d $pathtobot/bots/$user_id/$bot_name
dr=$(ls $pathtobot/bots/$user_id/$bot_name)
mv $pathtobot/bots/$user_id/$bot_name/$dr/* $pathtobot/bots/$user_id/$bot_name/

# create virtualenv and install essensial modules
python3 -m venv $pathtobot/bots/$user_id/$bot_name/venv
source $pathtobot/bots/$user_id/$bot_name/venv/bin/activate
pip3 install -r $pathtobot/bots/$user_id/$bot_name/requirements.txt
rm -rf $pathtobot/bots/$user_id/$bot_name/$dr

# create sh files
cat $pathtobot/backend/templates/start_bot > $pathtobot/bots/$user_id/$bot_name/start.sh
cat $pathtobot/backend/templates/stop_bot > $pathtobot/bots/$user_id/$bot_name/stop.sh
cat $pathtobot/backend/templates/check_process > $pathtobot/bots/$user_id/$bot_name/check_process.sh

exit 0
