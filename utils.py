import re
import json

import requests


def condense(string):
    return (re.sub(r'[^A-Za-z0-9]', '', string)).lower()


def login(username, password, challenge, challengekeyid):
    url = 'http://play.pokemonshowdown.com/action.php'
    values = {'act': 'login',
              'name': username,
              'pass': password,
              'challengekeyid': challengekeyid,
              'challenge': challenge
              }

    r = requests.post(url, data=values)

    print 'text', r.text

    try:
        response = json.loads(r.text[1:])  # the JSON response starts with a ]
    except:
        return None
    assertion = response['assertion']

    return assertion
