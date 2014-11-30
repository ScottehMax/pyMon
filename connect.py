import ConfigParser

import chatbot

if __name__ == '__main__':
    try:
        config = ConfigParser.ConfigParser()
        config.readfp(open('./config.ini'))

        ws = chatbot.Chatbot(config.get('Chatbot', 'server'),
                             protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
