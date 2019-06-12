#!/bin/bash
# This script prepare file structure for new user's bot
user_id=$1
arch=$2
pathtobot=$3
bot_name=${arch%.zip}

# make new dir and clean old files
mkdir $pathtobot/$user_id
mkdir $pathtobot/$user_id/$bot_name
rm -rf $pathtobot/$user_id/$bot_name/*

# unzip files
unzip $arch -d $pathtobot/$user_id/$bot_name
dr=$(ls $pathtobot/$user_id/$bot_name)
mv $pathtobot/$user_id/$bot_name/$dr/* $pathtobot/$user_id/$bot_name/
# create virtualenv and install essensial modules
python3 -m venv $pathtobot/$user_id/$bot_name/venv
source $pathtobot/$user_id/$bot_name/venv/bin/activate
pip3 install -r $pathtobot/$user_id/$bot_name/requirements.txt
rm -rf $pathtobot/$user_id/$bot_name/$dr 
exit 0
