#!/bin/bash
exec 1>installation.txt
exec 2>installation.txt
# This script prepare file structure for new user's bot
user_id=$1
arch=$2
pathtobot=$3
bot_name=${arch%.zip}

# make new dir and clean old files
if ! [ -d $pathtobot/bots/$user_id ]; then
    echo "Creating user directory..."
    mkdir $pathtobot/bots/$user_id
fi
if ! [ -d $pathtobot/bots/$user_id/$bot_name ]; then
    echo "Creating bot directory..."
    mkdir $pathtobot/bots/$user_id/$bot_name 
fi
echo "Cleaning bot folder..."
rm -rf $pathtobot/bots/$user_id/$bot_name/*

# unzip files
echo "Unpacking $arch"
unzip $pathtobot/download/$user_id/$arch -d $pathtobot/bots/$user_id/$bot_name
dr=$(ls $pathtobot/bots/$user_id/$bot_name)
mv $pathtobot/bots/$user_id/$bot_name/$dr/* $pathtobot/bots/$user_id/$bot_name/
echo "Unpacked to bots/$user_id/$bot_name/"

# create virtualenv and install essensial modules
echo "Creating virtual environment..."
python3 -m venv $pathtobot/bots/$user_id/$bot_name/venv
source $pathtobot/bots/$user_id/$bot_name/venv/bin/activate
echo "Installing essensial modules..."
pip3 install -r $pathtobot/bots/$user_id/$bot_name/requirements.txt
echo "Removing trash directory..."
rm -rf $pathtobot/bots/$user_id/$bot_name/$dr
echo "Creating log directory..."
mkdir $pathtobot/bots/$user_id/$bot_name/log

# create sh files
echo "Creating control-file..."
cat $pathtobot/backend/templates/bot > $pathtobot/bots/$user_id/$bot_name/bot.sh

mv installation.txt $pathtobot/bots/$user_id/$bot_name/
echo "Done"
exit 0
