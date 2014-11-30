from threading import Thread
from Queue import Queue
import time
import random

import utils


class ChatHandler:
    def __init__(self, cb):
        # these instance variables are just for convenience
        self.user = cb.user
        self.password = cb.password
        self.config = cb.config
        self.ws = cb

        self.currentusers = cb.currentusers

        self.initialise_queue()

    def initialise_queue(self):
        self.queue = Queue()
        queue_worker = Thread(target=self.run_queue,
                              name='message_queue',
                              args=[self.queue])
        queue_worker.start()

    def run_queue(self, queue):
        while True:
            msg = queue.get()
            self.ws.send(msg)
            time.sleep(0.6)

    def queue_message(self, msg):
        try:
            self.queue.put(msg)
        except AttributeError:
            print 'Queue not initialised'

    def send_msg(self, room, msg):
        if len(room) > 0 and room[0] == '>':
            room = room[1:]
        message = "%s|%s" % (room, msg)
        print '<<<', message
        self.queue_message(message)

    def send_pm(self, target, msg):
        self.send_msg('', '/pm %s, %s' % (target, msg))

    def handle(self, msg, room):
        if msg[0].lower == 'j':
            self.currentusers.append(msg[1])

        elif msg[0].lower == 'l':
            for user in self.currentusers:
                if utils.condense(user) == utils.condense(msg[1]):
                    self.currentusers.remove(user)

        elif msg[0].lower == 'n':
            newuser, olduser = msg[1], msg[2]
            for user in self.currentusers:
                if utils.condense(user) == utils.condense(msg[2]):
                    self.currentusers.remove(user)
                    self.currentusers.append(msg[1])

        elif msg[0] == 'users':
            self.currentusers = []
            for user in msg[1].split(',')[1:]:
                self.currentusers.append(user)
            print self.currentusers

        elif msg[0] == 'c:':
            # A few useless/humourous chatbot functions

            if msg[3] == 'who is a nerd':
                self.send_msg(room, '%s is a nerd' % random.choice(self.currentusers)[1:])
            elif utils.condense(msg[2]) == 'scotteh' and msg[3] == 'he':
                self.send_msg(room, 'has')
                self.send_msg(room, 'no')
                self.send_msg(room, 'style')
            elif utils.condense(msg[2]) == 'scotteh' and msg[3] == 'roll':
                self.send_msg(room, '!roll 100')
            elif utils.condense(msg[2]) == 'scotteh' and msg[3] == '!beacon':
                userlist = self.beacon(self.currentusers)
                for msg in userlist:
                    self.send_msg(room, msg)

        elif msg[0] == 'raw':
            if msg[1].startswith('<div class="infobox">Random number'):
                if msg[1][-7] == msg[1][-8] == msg[1][-9]:
                    self.send_msg(room, 'nice trips')
                elif msg[1][-7] == msg[1][-8]:
                    self.send_msg(room, 'nice dubs')

    def beacon(self, users):
        # Highlights every user in the room

        users2 = [] + users
        users2.reverse()
        string = ''
        msgs = []
        while not len(users2) == 0:
            if len(string) + len(users2[-1]) < 300:
                name = users2.pop()[1:]
                string += name + ' '
            else:
                msgs.append(string)
                string = ''
        msgs.append(string)
        return msgs
