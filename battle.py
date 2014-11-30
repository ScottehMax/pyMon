import json
import random

import utils
import battleutils


class BattleHandler:
    def __init__(self, ch):
        self.ch = ch
        self.battles = {}

    def handle(self, msg):

        battle_id = msg.pop(0)[1:-1]

        if battle_id not in self.battles:
            print battle_id, 'is new battle'
            self.new_battle(battle_id)

        try:
            if msg[0][0] != '|':
                msg[0] = '|' + msg[0]

            for part in '|'.join(msg).split('\n'):
                if part != '|':
                    self.battles[battle_id].handle(part.split('|')[1:])
                    
        except IndexError:
            err = 'list index out of range'

    def handle_challenge(self, msg):
        info = json.loads(msg[2])['challengesFrom']

        for who, battle_format in info.iteritems():
            print who, battle_format

            if battle_format in ['randombattle', 'challengecup1vs1']:
                self.ch.send_msg('', '/utm')
                self.ch.send_msg('', '/accept %s' % who)

    def new_battle(self, id):
        adapter = BattleAdapter({'id': id, 'ch': self.ch})
        self.battles[id] = adapter

class BattleAdapter:
    def __init__(self, args):
        self.id = args['id']
        self.ch = args['ch']
        self.rqid = 0

        # self.battle = battleutils.Battle({'id': self.id})

    def pick_alive_mons(self, sidedata):
        # Internal only. This prevents the bot from trying to send out a fainted mon

        alive_mons = []

        for i in range(6):
            if sidedata['pokemon'][i]['condition'] != '0 fnt':
                alive_mons.append(i + 1)

        return alive_mons

    def name_alive_mons(self, sidedata):
        alive_mons = []

        for i in range(6):
            if sidedata['pokemon'][i]['condition'] != '0 fnt':
                alive_mons.append(sidedata['pokemon'][i]['details'].split(', ')[0])

        return ', '.join(alive_mons)

    def pick_move(self, active):
        # Might add the main eval here later on

        possiblemoves = []

        if 'trapped' in active:
            return [active['moves'][0]['move']]

        for move in active['moves']:
            if move['pp'] > 0 and move['disabled'] == False:
                possiblemoves.append(move['move'])

        return possiblemoves


    def handle(self, msg):

        if msg[0] == 'init':
            self.ch.send_msg(self.id, '/timer')

        elif msg[0] == 'c':
            if utils.condense(msg[1]) == 'scotteh':
                if msg[2] == '!alive':
                    self.ch.send_msg(self.id, self.name_alive_mons(self.sidedata))

                elif msg[2] == '!moves':
                    self.ch.send_msg(self.id, ', '.join(self.pick_move(self.active)))

                elif msg[2].startswith('!custom'):
                    self.ch.send_msg(self.id, msg[2][8:])

        elif msg[0] == 'request':
            self.canMegaEvo = False
            request = json.loads(msg[1])

            if 'rqid' in request:
                self.rqid = request['rqid']

            if 'active' in request:
                self.active = request['active'][0]  # Note: check if active has multiple elements for doubles

            self.sidedata = request['side']
            self.player = self.sidedata['id']

            if 'canMegaEvo' in self.sidedata['pokemon'][0]:
                self.canMegaEvo = self.sidedata['pokemon'][0]['canMegaEvo']

        elif msg[0] == 'turn':
            if self.canMegaEvo:
                self.ch.send_msg(self.id, "/move %s mega|%s" % (random.choice(self.pick_move(self.active)), self.rqid))
            else:
                self.ch.send_msg(self.id, "/move %s" % random.choice(self.pick_move(self.active)))

        elif msg[0] == 'teampreview':
            self.ch.send_msg(self.id, "/team %s|%s" % (random.randint(1, 6), self.rqid))

        elif msg[0] == 'faint' and msg[1][0:2] == self.player:
            self.ch.send_msg(self.id, '/switch %s|%s' % (random.choice(self.pick_alive_mons(self.sidedata)), self.rqid))

        elif msg[0] == 'win':
            self.ch.send_msg(self.id, '/leave')

        elif msg[0] == '-crit' and msg[1][0:2] == self.player:
            self.ch.send_msg(self.id, 'wow stop hacking anytime')

        elif msg[0] == 'move':
            if msg[1][0:2] == self.player:
                if msg[2] in ['U-turn', 'Volt Switch', 'Baton Pass', 'Parting Shot']:  # Horrible hack
                    self.ch.send_msg(self.id, '/switch %s' % random.choice(self.pick_alive_mons(self.sidedata)[1:]))