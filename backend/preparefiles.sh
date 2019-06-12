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
echo "#!/bin/bash" > $pathtobot/bots/$user_id/$bot_name/start.sh
echo "venv/bin/python3 main.py > main.log 2>&1 &" >> $pathtobot/bots/$user_id/$bot_name/start.sh
echo "echo \$! > main.pid" >> $pathtobot/bots/$user_id/$bot_name/start.sh
exit 0
