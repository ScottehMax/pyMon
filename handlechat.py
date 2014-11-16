# PyMon
#
# Handles most chat messages

import json
import time
import random
import threading

import requests

import utils

def handle_message(ws, smsg):

    if smsg[0].startswith('>'):
        room = smsg[0][1:]

    elif smsg[0] == 'challstr':
        # login
        username = ws.user
        password = ws.password
        url = 'http://play.pokemonshowdown.com/action.php'
        values = {'act':'login',
                  'name':username,
                  'pass':password,
                  'challengekeyid':smsg[1],
                  'challenge':smsg[2]
                 }

        params = "act=login&name=%s&pass=%s&challengekeyid=%s&challenge=%s" % (username, password, smsg[1],smsg[2])
        print params
        print values['challengekeyid']
        r = requests.post(url, data=values)

        response = json.loads(r.text[1:])
        assertion = response['assertion']
            
        print "Trying to login with user %s..." % username     
            
        ws.send("|/trn %s,0,%s" % (username, assertion))

        print "Logged in!"
            
        t = threading.Timer(2.0, ws.join_room, [ws.room])
        t.start()
            
    elif smsg[0] == 'pm':
        handle_pm(ws, utils.condense(smsg[1]), smsg[3])
            
    elif smsg[0] == 'c:':
        #if utils.condense(smsg[2]) == 'scotteh':
        if 1 == 1:
            if smsg[3] == 'who is a fage':
                ws.send('showderp|%s is a fage' % random.choice(ws.currentusers))
                    
    elif smsg[0] == 'J':
        ws.currentusers.append(smsg[1])
            
    elif smsg[0] == 'L':
        for user in ws.currentusers:
            if utils.condense(user) == utils.condense(smsg[1]):
                ws.currentusers.remove(user)

    elif smsg[0] == 'N':
        newuser, olduser = smsg[1], smsg[2]
        for user in ws.currentusers:
            if utils.condense(user) == utils.condense(smsg[2]):
                ws.currentusers.remove(user)
                ws.currentusers.append(smsg[1])

    elif smsg[0] == 'users':
        ws.currentusers = []
        for user in smsg[1].split(',')[1:]:
            ws.currentusers.append(user)
        print ws.currentusers


def handle_pm(ws, sender, msg):
    if sender == 'scotteh':
        if msg.startswith('!'):
            smsg = msg[1:].split(' ')
            command, args = smsg[0], smsg[1:]
            handle_command(ws, command, args)

def handle_command(ws, command, args):	
    for case in utils.switch(command):
        if case('hello'):
            ws.send_pm('scotteh', 'hi there scotteh!!!')
