#!/bin/bash
cd /home/veyzz/bots/DeployMEbot/
python3 auto_start_bots.py
readarray ARRAY < toStart
for i in ${ARRAY[@]}
    do
        cd $i
        bash bot.sh start &
    done
