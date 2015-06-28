pyMon
=====

Pokémon Showdown! chatbot, programmed in Python.



## Installation

### Virtualenv (optional, but recommended):

First, make sure you have [Virtualenv](https://virtualenv.pypa.io/en/latest/) installed. If you can run bash scripts, run `make_venv.sh`. It will create a Virtualenv and download the requirements automatically. Otherwise, just create a Virtualenv the way you would normally, activate, then install the requirements as below.

### Without Virtualenv:

If you have [pip](https://pypi.python.org/pypi/pip) installed, you can just run the following from the working directory:

`pip install -r requirements.txt`

NB: You may be required to run pip as root.



## Running

Firstly, create a configuration file called `config.ini`, using `config-example.ini` as a base.

### Virtualenv:

Running `run_bot.sh` will create a new screen session (killing an old one if it exists), and start the bot in that screen session. You can modify the script to change what the name of the screen session will be. If you are unable to execute bash scripts, activate the Virtualenv as you would normally, then run `connect.py`.

### Without Virtualenv:

Run `connect.py` to start the bot.

--------

This project is licensed under the terms of the MIT license.
