#!/bin/bash
# This script prepare file structure for new user's bot
user_id=$1
req=$2
arch=$3
mkdir $user_id
if [ "$?" = 0 ]; then
  # create virtualenv and install essensial modules
  python3 -m venv ./$user_id/venv
  source ./$user_id/venv/bin/activate
  pip3 install -r $req
  # extract files
  mkdir ./$user_id/bot
  tar -C ./$user_id/bot -xzvf $arch 
else
  exit 1
fi

