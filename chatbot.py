import ConfigParser
import re

from ws4py.client.threadedclient import WebSocketClient

import utils
import chathandler

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
        
    def closed(self, code, reason=None):
        # Note: add automatic checking whether still connected and if not, attempt to reconnect... see ps-chatbot
        print "Closed down", code, reason

    def received_message(self, m):
        global battle_formats

        messages = str(m).split('\n')  # PS sometimes sends multiple messages split by newlines...

        if messages[0][0] == '>':
            room = messages[0][1:]

        for rawmessage in messages:
            print rawmessage
            message = rawmessage.split("|")

            if len(message) < 2: continue

            battlepattern = re.compile('>battle')

            if battlepattern.match(message[0]):
                self.bh.handle(message, ws)

            downmsg = message[1].lower()

            if downmsg == 'challstr':
                print '%s: Attempting to login...' % self.user
                data = {}
                assertion = utils.login(self.user, self.password, message[3], message[2])

                if assertion is None:
                    raise Exception('%s: Could not login' % self.user)

                self.send('|/trn %s,0,%s' % (self.user, assertion))

            elif downmsg == 'formats':
                data = '|'.join(message[2:])

                # the next line takes all of the formats data PS sends on connection and turns it into a list

                battle_formats = map(utils.condense, (re.sub(r'\|\d\|[^|]+', '' ,('|' + re.sub(r'[,#]', '', data)))).split('|'))[1:]
                print battle_formats

            elif downmsg == 'updateuser':
                if utils.condense(message[2]) == utils.condense(self.user):
                    print '%s: Logged in!' % self.user

                    for r in self.rooms:
                        print '%s: Joining room %s.' % (self.user, r)
                        self.send('|/join %s' % r)

            elif downmsg in ['c', 'c:', 'pm', 'j', 'n', 'l', 'users']:
                self.ch.handle(message[1:], room)
            elif downmsg == 'tournament':
                self.ch.handle_tournament(message)
            elif downmsg == 'updatechallenges':
                self.bh.handle_challenge(message)

        
    def parse_message(self, m):
        if len(m.split('|')) > 1:
            return m.split("|")[1:]  # Gets rid of the empty string
        else:
            return m.split("|")

