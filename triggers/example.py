from trigger import *


class Example(Trigger):

    def match(self, info):
        return info.get('what') == '!example'

    def response(self, info):
        return 'response string'

        # Can also return multiple messages in the form of a list
        # return ['this', 'is', 'response']
