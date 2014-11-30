import ConfigParser
import re

from ws4py.client.threadedclient import WebSocketClient

import utils
import chathandler
import battle


class Chatbot(WebSocketClient):

    def opened(self):

        print "Chatbot opened!"
        # load configuration
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open('./config.ini'))

        self.user = self.config.get('Chatbot', 'username')
        self.password = self.config.get('Chatbot', 'password')
        self.rooms = self.config.get('Chatbot', 'rooms').split(',')

        self.currentusers = []

        self.ch = chathandler.ChatHandler(self)
        self.bh = battle.BattleHandler(self.ch)

    def closed(self, code, reason=None):
        # Note: add automatic checking whether still connected
        # if not, attempt to reconnect...
        print "Closed down", code, reason

    def received_message(self, m):
        global battle_formats

        # PS sometimes sends multiple messages split by newlines...
        messages = str(m).split('\n')

        if messages[0][0] == '>':
            room = messages.pop(0)
        else:
            room = self.rooms[0]

        for rawmessage in messages:
            rawmessage = "%s\n%s" % (room, rawmessage)

            print rawmessage

            msg = rawmessage.split("|")

            BATTLE_REGEX = re.compile('>battle')

            if BATTLE_REGEX.match(msg[0]): 
                # print 'handling battle message', msg
                self.bh.handle(msg)

            if len(msg) < 2:
                continue

            downmsg = msg[1].lower()

            if downmsg == 'challstr':
                print '%s: Attempting to login...' % self.user
                data = {}
                assertion = utils.login(self.user, self.password, msg[3], msg[2])

                if assertion is None:
                    raise Exception('%s: Could not login' % self.user)

                self.send('|/trn %s,0,%s' % (self.user, assertion))

            elif downmsg == 'formats':
                data = '|'.join(msg[2:])

                # the next line takes all of the formats data PS sends on connection and turns it into a list

                battle_formats = map(utils.condense, (re.sub(r'\|\d\|[^|]+', '', ('|' + re.sub(r'[,#]', '', data)))).split('|'))[1:]
                print battle_formats

            elif downmsg == 'updateuser':
                if utils.condense(msg[2]) == utils.condense(self.user):
                    print '%s: Logged in!' % self.user

                    for r in self.rooms:
                        print '%s: Joining room %s.' % (self.user, r)
                        self.send('|/join %s' % r)

            elif downmsg in ['c', 'c:', 'pm', 'j', 'n', 'l', 'users', 'raw']:
                self.ch.handle(msg[1:], room)
            elif downmsg == 'tournament':
                # self.ch.handle_tournament(msg)
                print 'not implemented handle_tournament'
            elif downmsg == 'updatechallenges':
                self.bh.handle_challenge(msg)
                #print 'not implemented handle_challenge'

    def parse_message(self, m):
        if len(m.split('|')) > 1:
            return m.split("|")[1:]  # Gets rid of the empty string
        else:
            return m.split("|")
