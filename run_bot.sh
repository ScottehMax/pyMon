#!/bin/bash

SCRN=pymon
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

cd $DIR
read -d $'\x04' VENV < venvname

if screen -list | grep -q "$SCRN"; then
    echo -n "Attempting to kill old screen session..."
    screen -X -S $SCRN quit
    echo "done."
fi

echo -n "Creating new screen session..."
screen -dm -S $SCRN
sleep 1
screen -S $SCRN -p 0 -X stuff "$DIR/$VENV/bin/python connect.py
"
echo "done. Bot is running."
