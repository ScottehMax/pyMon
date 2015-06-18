import json
import random

import utils
import battleutils


class BattleHandler:

    def __init__(self, ch):
        self.ch = ch
        self.battles = {}

    def handle(self, msg):
        battle_id = msg.pop(0)[1:-1].split('\n')[0]

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

            if battle_format in ['randombattle', 'challengecup1v1']:
                self.ch.send_msg('', '/utm')
                self.ch.send_msg('', '/accept %s' % who)

    def new_battle(self, id):
        adapter = BattleAdapter({'id': id, 'ch': self.ch, 'bh': self})
        self.battles[id] = adapter


class BattleAdapter:

    def __init__(self, args):
        self.id = args['id']
        self.ch = args['ch']
        self.bh = args['bh']
        self.rqid = 0
        self.lastmove, self.waiting = None, False  # Bleugh

        self.battle = battleutils.Battle(id=self.id)

    def pick_alive_mons(self, sidedata):
        # This returns a list of the *INDEXES* of any alive mons

        alive_mons = []

        for i in range(6):
            if sidedata['pokemon'][i]['condition'] != '0 fnt':
                alive_mons.append(i + 1)

        return alive_mons

    def pick_best_switch(self, sidedata):
        alive_mons = []

        for i in range(6):
            if sidedata['pokemon'][i]['condition'] != '0 fnt':
                alive_mons.append(i + 1)

        for mon in [x for x in sidedata['pokemon']]:
            print mon

    def name_alive_mons(self, sidedata):
        alive_mons = []

        for i in range(6):
            if sidedata['pokemon'][i]['condition'] != '0 fnt':
                alive_mons.append(sidedata['pokemon'][i]['details'].split(', ')[0])

        return ', '.join(alive_mons)

    def best_move(self, active, types, target):
        movesinfo = self.pick_move(active)
        print movesinfo

        try:
            movelist = [x.get('id') for x in movesinfo]
        except Exception as e:
            print e
            movelist = movesinfo

        print movelist
        scores = [battleutils.calculate_move_score(active, types, target, x) for x in movelist]

        best_score = max(scores)
        best_move = movelist[scores.index(best_score)]
        if best_score >= 120:
            print 'Best score is %s - score %s' % (best_move, best_score)            
            return '/move ' + best_move
        else:
            b_switch = self.best_switch(active, self.sidedata, target)
            if b_switch != '/switch 1':
                b_mon_switch_id = b_switch.split('/switch ')[1]
                b_mon_switch = self.sidedata.get('pokemon')[int(b_mon_switch_id) - 1]
                b_mon_species = b_mon_switch.get('details').split(', ')[0]
                print 'Score not good enough. switching to %s' % b_mon_species
                return b_switch
            else:
                print 'No good other options. using %s' % best_move
                return '/move ' + best_move

    def best_switch(self, active, sidedata, target):
        print 'call to switch'
        highest_score = 0
        alive_mon_indexes = self.pick_alive_mons(sidedata)
        side_mon_info = sidedata.get('pokemon')

        # Loops through all mons, finds which has the highest score, and switches

        print alive_mon_indexes
        best_mon_index = alive_mon_indexes[0]

        for i in alive_mon_indexes:

            mon = side_mon_info[i - 1]
            mon_info = mon.get('details').split(', ')

            mon_species = utils.condense(mon_info[0])
            mon_level = mon_info[1][1:]
            try:
                mon_types = battleutils.POKEDEX.get(mon_species).get('types')
            except Exception as e:
                print e
                mon_types = ['Normal']

            movelist = mon.get('moves')

            scores = [battleutils.calculate_move_score(active, mon_types, target, x) for x in movelist]
            print movelist
            print scores
            best_score = max(scores)

            if best_score > highest_score:
                print 'best score %s is higher than highest score %s!' % (best_score, highest_score)
                highest_score = best_score
                best_move = movelist[scores.index(best_score)]
                print 'best move is %s!' % best_move
                best_mon = mon_species
                best_mon_index = i

        result = '/switch ' + str(best_mon_index)
        print result
        return result

    def pick_move(self, active):
        # Might add the main eval here later on

        possiblemoves = []

        if active is not None and 'trapped' in active:
            return [active['moves'][0]['move']]

        for move in active['moves']:
            if move.get('pp') > 0 and not move.get('disabled'):
                possiblemoves.append(move)

        print possiblemoves

        return possiblemoves

    def handle(self, msg):
        # Commenting out until I decide whether to properly integrate triggers in battle rooms with regular triggers.
        # self.ch.handle(msg, self.id)

        if msg[0] == 'init':
            self.ch.send_msg(self.id, '/timer')

        elif msg[0] == 'c':

            # These are hardcoded.

            if utils.condense(msg[1]) == 'scotteh':
                if msg[2] == '!alive':
                    self.ch.send_msg(self.id, self.name_alive_mons(self.sidedata))

                elif msg[2] == '!moves':
                    if self.active is not None:
                        self.ch.send_msg(self.id, ', '.join(self.pick_move(self.active)))

                elif msg[2] == '!item':
                    self.ch.send_msg(self.id, self.sidedata['pokemon'][0]['item'])

                elif msg[2].startswith('!custom'):
                    self.ch.send_msg(self.id, msg[2][8:])

                elif msg[2].startswith('.eval'):
                    expression = msg[2][6:]
                    try:
                        response = eval(expression)
                        self.ch.send_msg(self.id, response)
                    except Exception as e:
                        self.ch.send_msg(self.id, e)

        elif msg[0] == 'player':
            # Sets p1 and p2 in a new player object

            if msg[1] == 'p1':

                if msg[2] == self.ch.user:
                    # This is me
                    self.me = 'p1'
                else:
                    self.me = 'p2'

                self.battle.p1 = battleutils.Player(id=msg[1], username=utils.condense(msg[2]))
            else:
                self.battle.p2 = battleutils.Player(id=msg[1], username=utils.condense(msg[2]))

        elif msg[0] == 'poke':
            if msg[1] == 'p1':
                self.battle.add_to_team(self.battle.p1, msg[2])
            else:
                self.battle.add_to_team(self.battle.p2, msg[2])

        elif msg[0] == 'switch' or msg[0] == 'drag':
            # New mon was sent out
            if msg[1][0:2] != self.me:
                if self.waiting:
                    self.waiting = False
                    self.ch.send_msg(self.id, '/switch %s|%s' % (random.choice(self.pick_alive_mons(self.sidedata)),
                                                                 self.rqid))

                mon_info = msg[2].split(', ')
                mon_species = utils.condense(mon_info[0])
                mon_level = int(mon_info[1][1:])

                print 'Encountered a level %s %s' % (mon_level, mon_species)
                self.active_opponent = battleutils.Pokemon(species=mon_species, level=mon_level)
            else:
                mon_info = msg[2].split(', ')
                mon_species = utils.condense(mon_info[0])
                self.types = battleutils.POKEDEX[mon_species]['types']

        elif msg[0] == 'request':
            self.canMegaEvo = False
            request = json.loads(msg[1])

            self.rqid = request.get('rqid')
            self.active = request.get('active', [None])[0]  # Note: check if active has multiple elements for doubles

            self.sidedata = request.get('side')
            self.player = self.sidedata.get('id')

            self.canMegaEvo = self.sidedata.get('pokemon')[0].get('canMegaEvo')

        elif msg[0] == 'turn':
            # move_msg = '/move %s' % random.choice(self.pick_move(self.active))
            # move_msg = '/move %s' % self.best_move(self.active, self.types, self.active_opponent)
            move_msg = self.best_move(self.active, self.types, self.active_opponent)
            print 'move_msg is %s' % move_msg
            if move_msg.startswith('/move'):
                message = (move_msg + '|' if not self.canMegaEvo else move_msg + ' mega |') + str(self.rqid)
                self.ch.send_msg(self.id, message)
            else:
                self.ch.send_msg(self.id, move_msg)

        elif msg[0] == 'teampreview':
            self.ch.send_msg(self.id, "/team %s|%s" % (random.randint(1, 6), self.rqid))

        elif msg[0] == 'faint' and msg[1][0:2] == self.player:
            if self.lastmove in {'U-turn', 'Volt Switch'}:
                # The opponent needs to send out their 'mon first
                self.waiting = True
            else:
                mon_choice = self.best_switch(self.active, self.sidedata, self.active_opponent)
                self.ch.send_msg(self.id, '%s|%s' % (mon_choice, self.rqid))

        elif self.waiting and msg[0] == 'switch' and msg[1][0:2] != self.player:
            # Opponent has sent out their 'mon
            self.waiting = False
            self.ch.send_msg(self.id, '/switch %s|%s' % (random.choice(self.pick_alive_mons(self.sidedata)), self.rqid))

        elif msg[0] == 'win':
            self.ch.send_msg(self.id, '/leave')

        elif msg[0] == 'deinit':
            del self.bh.battles[self.id]

        elif msg[0] == '-crit' and msg[1][0:2] == self.player:
            self.ch.send_msg(self.id, 'wow stop hacking anytime')

        elif msg[0] == 'move':
            self.lastmove = msg[2]
            if msg[1][0:2] == self.player:
                if msg[2] in {'U-turn', 'Volt Switch', 'Baton Pass', 'Parting Shot'}:  # Horrible hack
                    self.ch.send_msg(self.id, '/switch %s' % random.choice(self.pick_alive_mons(self.sidedata)[1:]))
