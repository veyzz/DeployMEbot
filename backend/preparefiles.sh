#!/bin/bash
# This script prepare file structure for new user's bot
user_id=$1
arch=$2
bot_name=${arch%.zip}

# make new dir and clean old files
mkdir ../bots/$user_id
mkdir ../bots/$user_id/$bot_name
rm -rf ../bots/$user_id/$bot_name/*

# unzip files
unzip $arch -d ../bots/$user_id/$bot_name
dr=$(ls ../bots/$user_id/$bot_name)
mv ../bots/$user_id/$bot_name/$dr/* ../bots/$user_id/$bot_name/
# create virtualenv and install essensial modules
python3 -m venv ../bots/$user_id/$bot_name/venv
source ../bots/$user_id/$bot_name/venv/bin/activate
pip3 install -r ../bots/$user_id/$bot_name/requirements.txt
rm -rf ../bots/$user_id/$bot_name/$dr 
exit 0
