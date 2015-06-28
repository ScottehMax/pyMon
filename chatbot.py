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
        self.rooms = self.config.get('Chatbot', 'rooms').split(',')
        self.master = self.config.get('Chatbot', 'master')

        self.currentusers = {}

        self.ch = chathandler.ChatHandler(self)
        self.bh = battle.BattleHandler(self.ch)

    def setup(self, timeout=1):
        self.__init__(self.url, protocols=['http-only', 'chat'])
        self.connect()
        self.run_forever()

    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, m):
        # PS sometimes sends multiple messages split by newlines...
        messages = str(m).split('\n')

        if messages[0][0] == '>':
            room = messages.pop(0)
        else:
            room = '>lobby'

        for rawmessage in messages:
            is_battle = False
            rawmessage = "%s\n%s" % (room, rawmessage)

            print rawmessage

            msg = rawmessage.split("|")

            battle_regex = re.compile('>battle-')

            if battle_regex.match(msg[0]):
                # print 'handling battle message', msg
                self.bh.handle(msg)

            if len(msg) < 2:
                continue

            downmsg = msg[1].lower()

            # print msg, ' - ', is_battle, ' - ', downmsg

            if downmsg == 'challstr':
                print '%s: Attempting to login...' % self.user
                assertion = utils.old_login(self.user, 
                                            self.config.get('Chatbot', 'password'), 
                                            msg[3], 
                                            msg[2])
                #assertion = utils.login(self.user, 
                #                        self.config.get('Chatbot','password'), 
                #                        '|'.join(msg[2:]))

                if assertion is None:
                    raise Exception('%s: Could not login' % self.user)

                self.send('|/trn %s,0,%s' % (self.user, assertion))

            elif downmsg == 'formats':
                data = '|'.join(msg[2:])

                # this takes all of the formats data PS sends on connection 
                # and turns it into a list
                self.ch.battle_formats = map(utils.condense,
                                             (re.sub(r'\|\d\|[^|]+', '', ('|' + re.sub(r'[,#]', '', data)))
                                              ).split('|'))[1:]

            elif downmsg == 'updateuser':
                if utils.condense(msg[2]) == utils.condense(self.user):
                    # Bot has logged in.

                    print '%s: Logged in!' % self.user

                    self.ch.queue_worker.start()

                    for r in self.rooms:
                        print '%s: Joining room %s.' % (self.user, r)
                        self.ch.queue_message('|/join %s' % r)

            elif downmsg in ['c', 'c:', 'pm', 'j', 'n', 'l', 'users', 'raw', 
                             ':', 'init']:
                print 'match', downmsg
                print msg
                self.ch.handle(msg[1:], room)

            elif downmsg == 'tournament':
                # self.ch.handle_tournament(msg)
                print 'not implemented handle_tournament'

            elif downmsg == 'updatechallenges':
                self.bh.handle_challenge(msg)

    def parse_message(self, m):
        if len(m.split('|')) > 1:
            return m.split("|")[1:]  # Gets rid of the empty string
        else:
            return m.split("|")
