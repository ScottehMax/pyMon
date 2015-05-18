from triggers.trigger import Trigger
from utils import condense


class Eval(Trigger):

    def match(self, info):
        return condense(info.get('who')) == self.ch.ws.master and info.get('what').startswith('.eval ')

    def response(self, info):
        command = info.get('what')[6:]
        try:
            result = eval(command)
            return result
        except Exception as e:
            self.ch.send_pm(self.ch.ws.master, str(e) + ': ' + e.__doc__)
