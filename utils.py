import re
import json
import _jsonnet

import requests


def condense(string):
    return (re.sub(r'[^A-Za-z0-9]', '', string)).lower()


def old_login(username, password, challenge, challengekeyid):
    url = 'http://play.pokemonshowdown.com/action.php'
    values = {'act': 'login',
              'name': username,
              'pass': password,
              'challengekeyid': challengekeyid,
              'challenge': challenge
              }

    r = requests.post(url, data=values)

    try:
        response = json.loads(r.text[1:])  # the JSON response starts with a ]
    except Exception as e:
        print e
        return None
    assertion = response['assertion']

    return assertion


def login(username, password, challstr):
    url = 'http://play.pokemonshowdown.com/action.php'
    values = {'act': 'login',
              'name': username,
              'pass': password,
              'challstr': challstr
              }

    r = requests.post(url, data=values)

    try:
        response = json.loads(r.text[1:])  # the JSON response starts with a ]
    except Exception as e:
        print e
        return None
    assertion = response['assertion']

    return assertion


def print_info(obj):
    for attrib in dir(obj)[3:]:
        print attrib, '-', getattr(obj, attrib)


def get_thread():
    catalog_uri = "http://a.4cdn.org/vp/catalog.json"

    r = requests.get(catalog_uri)

    try:
        catalog = json.loads(r.text)
    except ValueError:
        print "Unable to decode the response"
        return False

    newest_thread = {'no': 0, 'last_reply_time': 0}

    for page in catalog:
        for thread in page['threads']:
            if (('showderp' in thread.get('sub', '').lower()) or
               ('showderp' in thread.get('name', '').lower()) or
               ('showderp' in thread.get('com', '').lower())) and thread.get('last_replies'):

                reply_time = thread['last_replies'][-1]['time']

                if reply_time > newest_thread['last_reply_time']:
                    newest_thread['no'] = thread['no']
                    newest_thread['last_reply_time'] = reply_time

    return newest_thread


def get_rank(user, room, ch):
    if room not in ch.current_users:
        return False
    else:
        for r_user in ch.current_users[room]:
            if condense(user) == condense(r_user):
                result = r_user[0]
                return result
        return False


def get_battle(ch):
        battle_regex = "((https?\\:\\/\\/)?(play\\.pokemonshowdown\\.com|.*?\\.psim\\.us)\\/(battle-(?:FORMATS)\\-\\d{1,9}))"
        real_regex = re.compile(battle_regex.replace('FORMATS', '|'.join(ch.battle_formats)))

        thread_info = get_thread()

        if not thread_info:
            return False

        battle = False

        if not thread_info or thread_info['no'] == 0:
            return False

        r = requests.get('http://a.4cdn.org/vp/res/%s.json' % thread_info['no'])

        try:
            thread = json.loads(r.text)
        except ValueError:
            print "Unable to load battle response"
            return False

        for post in thread['posts']:
            if post.get('com'):
                m = real_regex.search(post.get('com').replace('<wbr>', ''))
                if m:
                    battle = [m.groups()[3], post['time']]

        return battle


def load_js_obj_literal(j):
    """Terrible hack."""
    j = j[j.index('{'):]
    j = j.replace('\n', '').replace('\t', '')
    j = j.replace(';', '')
    j = re.sub(r'//.*?{', r'{', j)
    result = json.loads(_jsonnet.evaluate_snippet('snippet', j))
    return result
