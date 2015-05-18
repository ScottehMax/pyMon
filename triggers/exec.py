from triggers.trigger import Trigger
from utils import condense


class Exec(Trigger):

    def match(self, info):
        return condense(info.get('who')) == self.ch.ws.master and info.get('what').startswith('.exec ')

    def response(self, info):
        command = info.get('what')[6:]
        room = info.get('room', '')
        try:
            exec command
            self.ch.send_pm(self.ch.ws.master, 'Success!')
        except Exception as e:
            self.ch.send_pm(self.ch.ws.master, str(e) + ': ' + e.__doc__)
