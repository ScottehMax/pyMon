#!/bin/bash

# enter name for virtualenv
read -p "Enter the name for the virtualenv [venv]: " venvname
venvname=${venvname:-venv}

echo "Creating venv with name $venvname"
virtualenv $venvname

# making a little file here so we know what the venv is called (prevents using
# an environment variable)
echo "$venvname" > venvname

echo -n "Activating... "
source $venvname/bin/activate
echo "done."

echo "Installing requirements..."
pip install -r requirements.txt

echo "Finished! You can now run run_bot.sh to start the bot in a screen session."
