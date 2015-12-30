from threading import Thread
from Queue import Queue
from itertools import groupby
import time
import os
import imp
import inspect

import redis
import concurrent.futures as futures

from utils import condense


class ChatHandler:
    """Deals with most of the chat messages."""

    def __init__(self, cb):
        # these instance variables are just for convenience
        self.user = cb.user
        self.config = cb.config
        self.ws = cb
        self.thread_pool_executor = futures.ThreadPoolExecutor(max_workers=20)

        self.triggers = []
        self.join_time = {}

        self.current_users = cb.currentusers

        self.battling = False  # self.config.get('Chatbot', 'battle')

        try:
            redis_uname = self.config.get('External', 'redis_uname')
            redis_pass = self.config.get('External', 'redis_pass')
            redis_server = self.config.get('External', 'redis_server')
            redis_url = os.getenv('REDISTOGO_URL', 'redis://%s:%s@%s' %
                                  (redis_uname, redis_pass, redis_server))

            self.redis = redis.from_url(redis_url)
            # self.redis = redis.from_url('redis://127.0.0.1:6379')
        except Exception as e:
            print e
            print "Redis connection failed (ignore if you're not using redis)"

        self.initialise_triggers(self.config)
        self.initialise_queue()

    def initialise_triggers(self, config):
        """Loads all triggers as specified in config."""
        trigger_list = config.get('Chatbot', 'triggers').split(',')

        print trigger_list  # debug

        for trigger_filename in trigger_list:
            modname, ext = os.path.splitext(trigger_filename)
            trigger_file, path, descr = imp.find_module(modname, ['./triggers'])

            if trigger_file:
                mod = imp.load_module(modname, trigger_file, path, descr)
                # This isn't very good... investigate a better solution.
                self.triggers.append([x for x in inspect.getmembers(mod)[0:2] if x[0] != 'Trigger'][0][1](self))
            else:
                print 'Error loading Trigger %s' % trigger_filename

        print self.triggers

    def initialise_queue(self):
        self.queue = Queue()
        self.queue_worker = Thread(target=self.run_queue,
                                   name='message_queue',
                                   args=[self.queue])
        self.queue_worker.daemon = True
        # queue_worker.start()
        # self.battle_thread = Thread(target=self.battling_queue,
        #                             name='battling_queue')
        # battle_thread.start()

    def run_queue(self, queue):
        while True:
            msg = queue.get()
            if msg is not None:
                self.ws.send(msg)
            time.sleep(0.6)

    def battling_queue(self):
        while True:
            while self.battling:
                print 'Searching for a new battle...'
                self.queue_message('|/utm')
                self.queue_message('|/search randombattle')
                time.sleep(30)

    def queue_message(self, msg):
        try:
            self.queue.put(msg)
        except AttributeError:
            print 'Queue not initialised'

    def send_msg(self, room, msg):
        if len(room) > 0 and room[0] == '>':
            room = room[1:]
        message = "%s|%s" % (room, msg)
        self.queue_message(message)

    def send_pm(self, target, msg):
        self.send_msg('', '/pm %s, %s' % (target, msg))

    def call_trigger_response(self, trigger, m_info):
        try:
            response = trigger.response(m_info)
            return response
        except Exception as e:
            self.send_pm(self.ws.master,
                         "Crashed: %s, %s, %s, %s" %
                         (e.message, e.args, trigger, type(e)))

    def future_callback(self, future):
        response = future.result()
        room = future.room
        m_info = future.m_info

        if response:
            who = m_info['who']
            if type(response) != list:
                response = [response]
            for s_response in response:
                if m_info['where'] == 'pm':
                    s_response = '/pm %s, %s' % (who, s_response)
                self.send_msg(room, s_response)

    def handle(self, msg, room):
        room = room.replace('>', '')

        m_info = self.make_msg_info(msg, room, self.ws)

        if m_info['where'] == ':':
            # : messages contain an UNIX timestamp of when the room was joined
            # nvm, PS's time is usually off
            self.join_time[room] = str(int(time.time()))

        # Prevents the chatbot from responding to messages
        # sent before it entered the room
        if (m_info.get('who') and
            ((m_info.get('when') and
             int(m_info.get('when')) > int(self.join_time[room])) or
             m_info.get('where') in {'j', 'l', 'pm'})):

            for trigger in self.triggers:
                # print 'testing trigger %s' % trigger
                try:
                    if trigger.match(m_info):
                        print 'match %s' % trigger
                        future = self.thread_pool_executor.submit(self.call_trigger_response, trigger, m_info)
                        future.room = room
                        future.m_info = m_info
                        future.add_done_callback(self.future_callback)
                except Exception as e:
                    self.send_pm(self.ws.master,
                                 "Crashed in match: %s, %s, %s" %
                                 (e.message, e.args, trigger))

        # User list is currently hardcoded here. Might move this to triggers later on
        if m_info['where'] == 'j' and condense(m_info['who']) not in map(condense, self.current_users[room]):
            self.current_users[room].append(msg[1])

        elif m_info['where'] == 'l':
            for user in self.current_users[room]:
                if condense(user) == condense(msg[1]):
                    self.current_users[room].remove(user)

        elif m_info['where'] == 'n':
            # |N| messages are of the format |N|(rank)newname|oldnameid
            # Rank is a blank space if the nick is a regular user
            # i.e. |N|@Scotteh|stretcher
            newuser, olduser, userfound = msg[1], msg[2], False
            for user in self.current_users[room]:
                if condense(user) == condense(msg[2]):
                    self.current_users[room].remove(user)
                    userfound = True
            if userfound:
                self.current_users[room].append(msg[1])

        elif m_info['where'] == 'users':
            # Resets the userlist for the room if it exists, and creates a new one
            # |users| messages are only sent on room join
            self.current_users[room] = []
            for user in msg[1].split(',')[1:]:
                self.current_users[room].append(user)

        if m_info['where'] == 'raw' and int(time.time()) > int(self.join_time[room]):
            print (int(time.time()), self.join_time[room])
            # Get checker. Hardcoded.
            getmap = {2: 'dubs',
                      3: 'trips',
                      4: 'quads',
                      5: 'quints',
                      6: 'sexts',
                      7: 'septs',
                      8: 'octs',
                      9: 'nons',
                      10: 'decs'}

            if m_info['all'][1].startswith('<div class="infobox">Roll '):
                if '+' in m_info['all'][1]:
                    # dirty cheaters, trying to fake GETs
                    return
                raw_msg = msg[1][21:-6]  # Strips the leading HTML

                # Don't try and understand the next line, it takes raw_msg as input and 
                # creates a list of size 2 lists splitting the raw_msg and showing the consecutive 
                # characters, and returns the amount of consecutive characters at the end
                # '11223344441122' => [['1', 2], ['2', 2], ['3', 2], ['4', 4], ['1', 2], ['2', 2]]
                get = getmap.get([[k,len(list(g))] for k, g in groupby(raw_msg)][-1][1])
                if get:
                    self.send_msg(room, 'nice ' + get)

    def make_msg_info(self, msg, room, ws):
        info = {'where': msg[0],
                'ws': ws,
                'all': msg,
                'ch': self,
                'me': self.user
                }

        info['where'] = info['where'].lower()

        if info['where'] == 'c:':
            info.update({'where': 'c',
                         'room': room,
                         'who': msg[2].decode('utf-8')[1:].encode('utf-8'),
                         'allwho': msg[2],
                         'when': str(int(time.time())),
                         'what': '|'.join(msg[3:])})

        elif info['where'] == 'c':
            info.update({'room': room,
                         'who': msg[1].decode('utf-8')[1:].encode('utf-8'),
                         'allwho': msg[1],
                         'what': '|'.join(msg[2:])})

        elif info['where'] == 'j' or info['where'] == 'l':
            info.update({'room': room,
                         'who': msg[1][1:],
                         'allwho': msg[1],
                         'what': ''})

        elif info['where'] == 'n':
            info.update({'room': room,
                         'who': msg[1][1:],
                         'allwho': msg[1],
                         'oldname': msg[2],
                         'what': ''})

        elif info['where'] == 'users':
            info.update({'room': room,
                         'who': '',
                         'what': msg[1]})

        elif info['where'] == 'pm':
            info.update({'who': msg[1][1:],
                         'allwho': msg[1],
                         'target': msg[2][1:],
                         'what': msg[3]})

        return info
