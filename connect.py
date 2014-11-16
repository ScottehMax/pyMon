import ConfigParser

from ws4py.client.threadedclient import WebSocketClient

import utils
import handlechat

class Chatbot(WebSocketClient):

    def opened(self):
        print "Chatbot opened!"
        config = ConfigParser.ConfigParser()
        config.readfp(open('./config.ini'))

        self.user = config.get('Chatbot', 'username')
        self.password = config.get('Chatbot', 'password')
        self.room = config.get('Chatbot', 'room')

        self.currentusers = []
        
    def closed(self, code, reason=None):
        print "Closed down", code, reason

    def received_message(self, m):
        #print repr(str(m))
        msgs = str(m).split('\n')  # PS sometimes sends multiple messages split by newlines...
        for message in msgs:
            print message
            smsg = self.parse_message(message)
            #print smsg
            handlechat.handle_message(self, smsg)
        
    def parse_message(self, m):
        if len(m.split('|')) > 1:
            return m.split("|")[1:]  # Gets rid of the empty string
        else:
            return m.split("|")

    def join_room(self, room):
        self.send("|/join " + room)

    def send_msg(self, room, msg):
        self.send("%s|%s" % (room, msg))

    def send_pm(self, target, msg):
        self.send_msg('', '/pm %s, %s' % (target, msg))

if __name__ == '__main__':
    try:
        ws = Chatbot('ws://127.0.0.1:8000/showdown/websocket', protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
