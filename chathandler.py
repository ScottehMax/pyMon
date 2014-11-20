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
        queue_worker = Thread(target=self.run_queue, name='message_queue', args=[self.queue])
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
        self.queue_message("%s|%s" % (room, msg))

    def send_pm(self, target, msg):
        self.send_msg('', '/pm %s, %s' % (target, msg))

    def handle(self, message, room='lobby'):
        if message[0].lower == 'j':
            self.currentusers.append(message[1])

        elif message[0].lower == 'l':
            for user in self.currentusers:
                if utils.condense(user) == utils.condense(message[1]):
                    self.currentusers.remove(user)

        elif message[0].lower == 'n':
            newuser, olduser = message[1], message[2]
            for user in self.currentusers:
                if utils.condense(user) == utils.condense(message[2]):
                    self.currentusers.remove(user)
                    self.currentusers.append(message[1])

        elif message[0] == 'users':
            self.currentusers = []
            for user in message[1].split(',')[1:]:
                self.currentusers.append(user)
            print self.currentusers

        elif message[0] == 'c:':
            if message[3] == 'who is a nerd':
                self.send_msg(room, '%s is a nerd' % random.choice(self.currentusers))
            elif utils.condense(message[2]) == 'scotteh' and message[3] == 'he':
                self.send_msg(room, 'has')
                self.send_msg(room, 'no')
                self.send_msg(room, 'style')



