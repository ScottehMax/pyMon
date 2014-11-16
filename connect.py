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
            smsg = handlechat.parse_message(self, message)
            #print smsg
            handlechat.handle_message(self, smsg)

    def join_room(self, room):
        self.send("|/join " + room)

if __name__ == '__main__':
    try:
        ws = Chatbot('ws://127.0.0.1:8000/showdown/websocket', protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
