#!/bin/bash
# This script prepare file structure for new user's bot

# write stdout and strerr to file
log_file=installation$(date +%s)$RANDOM.log
exec 1>$log_file
exec 2>$log_file

# read args
user_id=$1
bot_id=$2
arch=$3
pathtobot=$4
bot_name=${arch%.zip}

# make new dir and clean old files
if ! [ -d $pathtobot/bots/$user_id ]; then
    echo "Creating user directory..."
    mkdir $pathtobot/bots/$user_id
fi
if ! [ -d $pathtobot/bots/$user_id/$bot_name ]; then
    echo "Creating bot directory..."
    mkdir $pathtobot/bots/$user_id/$bot_name
else
    if [ -f $pathtobot/bots/$user_id/$bot_name/bot.sh ]; then
        echo "DADA YA"
fi
echo "Cleaning bot folder..."
rm -rfv $pathtobot/bots/$user_id/$bot_name/*

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
pip3 install --no-cache-dir -r $pathtobot/bots/$user_id/$bot_name/requirements.txt
echo "Removing trash directory..."
rm -rfv $pathtobot/bots/$user_id/$bot_name/$dr
echo "Creating log directory..."
mkdir $pathtobot/bots/$user_id/$bot_name/log

# create sh files
echo "Creating control-file..."
cat $pathtobot/backend/templates/bot > $pathtobot/bots/$user_id/$bot_name/bot.sh
cat $pathtobot/backend/templates/handler > $pathtobot/bots/$user_id/$bot_name/handler.sh
chmod +x $pathtobot/bots/$user_id/$bot_name/bot.sh

echo $bot_id > $pathtobot/bots/$user_id/$bot_name/bot.id
mv $log_file $pathtobot/bots/$user_id/$bot_name/log/installation.log
echo "Done"
exit 0
