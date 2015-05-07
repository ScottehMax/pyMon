import re
import json
from pyparsing import (Suppress, Regex, quotedString, Word, alphas,
                       alphanums, oneOf, Forward, Optional, dictOf, delimitedList, Group, removeQuotes)

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


def load_js_obj_literal(j):
    """Terrible hack."""
    j = j[j.index('{'):]
    j = j.replace('\n', '').replace('\t', '')
    j = j.replace(';', '')
    j = re.sub(r'//.*?{', r'{', j)
    LBRACK, RBRACK, LBRACE, RBRACE, COLON, COMMA = map(Suppress,"[]{}:,")
    integer = Regex(r"[+-]?\d+").setParseAction(lambda t:int(t[0]))
    real = Regex(r"[+-]?\d+\.\d*").setParseAction(lambda t:float(t[0]))
    string_ = Word(alphas,alphanums+"_") | quotedString.setParseAction(removeQuotes)
    bool_ = oneOf("true false").setParseAction(lambda t: t[0]=="true")
    item = Forward()
    key = string_
    dict_ = LBRACE - Optional(dictOf(key+COLON, item+Optional(COMMA))) + RBRACE
    list_ = LBRACK - Optional(delimitedList(item)) + RBRACK
    item << (real | integer | string_ | bool_ | Group(list_ | dict_ ))
    result = item.parseString(j,parseAll=True)[0]
    return result
