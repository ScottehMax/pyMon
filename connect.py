import ConfigParser
import threading
import time
import logging

import chatbot


def runbot(t):
    config = ConfigParser.ConfigParser()
    config.readfp(open('./config.ini'))

    ws = chatbot.Chatbot(config.get('Chatbot', 'server'),
                         protocols=['http-only', 'chat'])
    try:
        ws.connect()
        ws.run_forever()
    except Exception as e:
        print 'Exception: {0}\nArguments:\n{1!r}'.format(type(e).__name__,
                                                         e.args)
        logging.error('Exception: {0}\nArguments:\n{1!r}'.format(type(e).__name__,
                                                                 e.args))
        print 'Unable to connect. Timing out for %s seconds...' % t
        time.sleep(t)
        runbot(t+2)

if __name__ == '__main__':
    # set up error logging
    logging.basicConfig(filename='error.log',
                        level=logging.WARNING,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        )

    while True:
        try:
            if 'chatbot' not in [x.name for x in threading.enumerate()]:
                logging.info('Bot thread created')
                bot = threading.Thread(target=runbot,
                                       name='chatbot',
                                       args=([2]))
                # Entire program exits when there are only daemon threads
                bot.daemon = True
                bot.start()
            time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            # Entire program will exit, since MainThread is the only
            # non-daemon thread -- The sole purpose of this is so CTRL+C etc.
            # will close the whole program
            logging.info('Bot closed by KeyboardInterrupt or SystemExit')
            exit()
